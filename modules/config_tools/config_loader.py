from pathlib import Path
from typing import Union, Optional, Dict, Tuple
import yaml
import json
import logging
from datetime import date, datetime

from .config_validator import ConfigValidator
from .prepare_logger import prepare_logger
from .utils import SensitiveDict, CustomJSONEncoder, normalize_key 

class ConfigLoader:
    """Class to load and validate configuration from YAML files."""
    
    def __init__(self, config_path: Union[str, Path], rules_dir: Optional[Union[str, Path]] = None):
        """Initialize ConfigLoader, load and validate the configuration."""
        try:
            self.config_path: Path = self.ensure_path_object(config_path)
            self.validate_yaml_path(self.config_path)
            self.config: Optional[Dict] = self.extract_config_from_yaml(self.config_path)

            if rules_dir:
                self.rule_path: Path = self.ensure_path_object(rules_dir)
                if not self.rule_path.is_dir():
                    raise ValueError(f"Provided rules path {self.rule_path} is not a valid directory.")
                
                # Load both config_rules and auth_rules from the given directory
                self.config_rules, self.auth_rules = self.load_rules(rules_dir)
            else:
                self.config_rules, self.auth_rules = self.load_rules()



            log_path = self.get_log_path()
            log_name_prefix = self.get_log_name_prefix()
            self.logger = prepare_logger(log_path, log_name_prefix)
            self.logger.info(f"Logger initialized with log output directory: '{log_path}'")

            self.config["logger"] = self.logger

            if self.config is not None:
                self.validate_config(self.config)
                self.logger.info("Config validated successfully")

            if 'authentication_path' in self.config:
                auth_path = self.config['authentication_path']
                self.load_authentication_config(auth_path)
                self.logger.info(f"Authentication config loaded from '{auth_path}'")

                # self.config['config_validation_rules'] = self.config_rules
                # self.config['auth_validation_rules'] = self.auth_rules
                self.logger.info(f'Config loaded successfully. Loaded config:\n {json.dumps(self.config, indent=4, cls=CustomJSONEncoder)}')

        except (FileNotFoundError, IsADirectoryError, ValueError, yaml.YAMLError) as e:
            raise e


    def load_rules(self, rules_dir: Optional[Union[str, Path]] = None) -> Tuple[Dict, Dict]:
        """Load both config_rules and auth_rules from the specified directory, defaults to 'configs/validation/'."""
        config_rules = {}
        auth_rules = {}

        # Set default rules directory if none is provided
        if rules_dir is None:
            rules_dir = Path("configs/validation")
        
        # Check for config_rules.yaml
        config_rules_path = Path(rules_dir) / "config_rules.yaml"
        if config_rules_path.exists():
            validator = ConfigValidator({}, config_rules_path)
            config_rules = validator.rules
        else:
            self.logger.warning(f"config_rules.yaml not found at {config_rules_path}")
        
        # Check for auth_rules.yaml
        auth_rules_path = Path(rules_dir) / "auth_rules.yaml"
        if auth_rules_path.exists():
            validator = ConfigValidator({}, auth_rules_path)
            auth_rules = validator.rules
        else:
            self.logger.warning(f"auth_rules.yaml not found at {auth_rules_path}")
        
        return config_rules, auth_rules


    def get_config(self) -> Dict:
        """Return the loaded configuration."""
        return self.config

    def get_log_path(self) -> str:
        """Return the log path, or 'logs/' if not specified or invalid."""
        log_path = self.config.get('log_output_path', 'logs') if self.config else 'logs'
        log_path = Path(log_path)

        if log_path.exists():
            if log_path.is_file():
                log_path = Path('logs')
                log_path.mkdir(parents=True, exist_ok=True)
        else:
            log_path.mkdir(parents=True, exist_ok=True)

        return str(log_path) if log_path.is_dir() else str(Path('logs').mkdir(parents=True, exist_ok=True))

    def get_log_name_prefix(self) -> str:
        """Return the log name prefix from the config."""
        return self.config.get('log_name_prefix', self.config.get('log name prefix', ''))

    def ensure_path_object(self, path_string_or_path: Union[str, Path]) -> Path:
        """Convert a string or Path object to a normalized Path object."""
        if isinstance(path_string_or_path, str):
            return Path(path_string_or_path).resolve()
        elif isinstance(path_string_or_path, Path):
            return path_string_or_path.resolve()
        else:
            raise ValueError("Provided path must be a string or Path object")

    def validate_yaml_path(self, path: Path) -> None:
        """Validate that the path exists, is a file, and is a YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"The file '{path}' does not exist.")
        if not path.is_file():
            raise IsADirectoryError(f"'{path}' is a directory, not a file.")
        if not path.suffix == ".yaml":
            raise ValueError(f"'{path}' is not a YAML file. Must end with .yaml.")
                
    def extract_config_from_yaml(self, path: Path) -> Optional[Dict]:
        """Extract and normalize configuration from a YAML file."""
        try:
            with open(path, 'r') as file:
                config_data = yaml.safe_load(file)

                if not isinstance(config_data, dict):
                    raise ValueError("YAML file content is not a valid dictionary.")

                # Normalize each key using the utility function
                return {normalize_key(key): value for key, value in config_data.items()}

        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")

    def validate_config(self, config: Dict) -> None:
        """Validate the config using the provided config_rules."""
        try:
            validator = ConfigValidator(config, None)
            validator.rules = self.config_rules  # Set the config_rules loaded earlier
            validator.validate()
        except ValueError as e:
            self.logger.error(f"Config validation error: {e}")
            raise ValueError(f"Config validation error: {e}")

    def load_authentication_config(self, auth_path: str) -> None:
        """Load and validate the authentication config from the specified path."""
        auth_path_obj = Path(auth_path)
        if not auth_path_obj.exists() or not auth_path_obj.is_file():
            raise FileNotFoundError(f"Authentication path '{auth_path}' does not exist or is not a valid file.")

        auth_config = self.extract_config_from_yaml(auth_path_obj)
        if auth_config:
            self.config["auth"] = SensitiveDict(auth_config)
            self.logger.info("Authentication data loaded into config")

        validator = ConfigValidator(self.config['auth'].get_data(), None)
        validator.rules = self.auth_rules  # Set the auth_rules loaded earlier
        validator.validate()
        self.logger.info("Authentication data validated successfully")
