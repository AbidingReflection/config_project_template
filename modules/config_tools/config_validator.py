import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, date, timedelta
import re
from .utils import normalize_key  # Import the normalize_key function

class ConfigValidator:
    """Class to validate configuration against a set of rules."""
    
    def __init__(self, config: Dict[str, Any], rules_file: Optional[Union[str, Path]] = None):
        """Initialize the validator with config and load rules from YAML if provided."""
        self.config = config
        self.errors = []
        self.rules = {}

        if rules_file:
            self.load_rules_from_path(Path(rules_file))

    def load_rules_from_path(self, rules_path: Path) -> None:
        """Load validation rules from a YAML file using a Path object."""
        if not rules_path.is_file():
            raise ValueError(f"Rules file {rules_path} does not exist or is not a file.")
        
        with rules_path.open('r') as f:
            self.rules = yaml.safe_load(f)
        
        if not isinstance(self.rules, dict):
            raise ValueError(f"Rules file {rules_path} must contain a valid dictionary of rules.")
        
        # Normalize the keys for consistency
        self.rules = {normalize_key(key): value for key, value in self.rules.items()}


    def dump_config_to_yaml(self, output_path: Path) -> None:
        """Dump the config dictionary as a nicely formatted YAML file."""
        with output_path.open('w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)


    def validate(self) -> None:
        """Run validation on the config."""
        if not self.rules:
            raise ValueError("No validation rules found. Please load rules from a file or pass them directly.")

        # Define keys that should be ignored during validation
        ignored_keys = {"config_validation_rules", "auth_validation_rules", "logger"}

        # Check for any unexpected keys in the config that are not present in the rules, excluding ignored keys
        extra_keys = set(self.config.keys()) - set(self.rules.keys()) - ignored_keys
        if extra_keys:
            raise ValueError(f"Config validation error: Unexpected config keys found: {', '.join(extra_keys)}")

        for key, rule in self.rules.items():
            value = self.config.get(key)

            # Check if the field is required and missing
            if rule.get('required', False) and value is None:
                self.errors.append(f"Missing required config key: '{key}'")
                continue  # Skip further validation if missing

            # Ensure validation rules are supplied
            validators = rule.get('validation', None)
            if validators is None or len(validators) == 0:
                raise ValueError(f"No validation rules supplied for config key: '{key}'")

            # Run each validation rule if the field exists
            if value is not None:
                for validation in validators:
                    if isinstance(validation, str):  # Direct function call without parameters
                        validator = getattr(self, validation, None)
                        if validator:
                            try:
                                validator(key, value)
                            except ValueError as e:
                                self.errors.append(str(e))
                        else:
                            raise ValueError(f"Validation method '{validation}' not found for key: '{key}'")
                    elif isinstance(validation, dict):  # Validation with parameters
                        for validator_name, params in validation.items():
                            validator = getattr(self, validator_name, None)
                            if validator:
                                try:
                                    validator(key, value, **params)  # Pass parameters to the validator
                                except ValueError as e:
                                    self.errors.append(str(e))
                            else:
                                raise ValueError(f"Validation method '{validator_name}' not found for key: '{key}'")

        if self.errors:
            raise ValueError("\n".join(self.errors))




    @staticmethod
    def validate_https_url(key: str, value: str) -> None:
        """Validate that a URL starts with 'HTTPS://' and ends with '/'."""
        if not value.lower().startswith('https://'):
            raise ValueError(f"Config key '{key}' must start with 'HTTPS://'. Found: '{value}'")
        if not value.endswith('/'):
            raise ValueError(f"Config key '{key}' must end with '/'. Found: '{value}'")

    @staticmethod
    def validate_log_prefix(key: str, value: str) -> None:
        """Validate that a log prefix ends with an underscore."""
        if not value.lower().endswith('_'):
            raise ValueError(f"log_name_prefix '{key}' must end with '_'. Found: '{value}'")

    @staticmethod
    def validate_int_range(key: str, value: int, min_value: Optional[int] = None, max_value: Optional[int] = None) -> None:
        """Validate that an integer falls within the given range."""
        if min_value is not None and value < min_value:
            raise ValueError(f"Config key '{key}' must be greater than or equal to {min_value}. Found: {value}")
        if max_value is not None and value > max_value:
            raise ValueError(f"Config key '{key}' must be less than or equal to {max_value}. Found: {value}")

    @staticmethod
    def validate_non_empty_string(key: str, value: str) -> None:
        """Validate that the string is non-empty."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Config key '{key}' must be a non-empty string. Found: '{value}'")

    @staticmethod
    def validate_qTest_bearer_token(key: str, value: str) -> None:
        """Validate that the value is a valid qTest Bearer Token."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Config key '{key}' must be a non-empty string. Found: '{value}'")
        
        bearer_token_pattern = re.compile(r'^Bearer [a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$')
        if not bearer_token_pattern.fullmatch(value):
            raise ValueError(f"Auth Config key '{key}' must be a Bearer Token in the format 'Bearer <UUID>'. Found: '{value}'")

    @staticmethod
    def validate_date(key: str, value: Union[str, date], min_date: Optional[str] = None) -> None:
        """Validate that the date is on or after the minimum date."""
        try:
            if isinstance(value, str):
                value_date = datetime.strptime(value, "%Y-%m-%d").date()
            elif isinstance(value, date):
                value_date = value
            else:
                raise ValueError(f"Config key '{key}' must be a valid date in the format YYYY-MM-DD or a date object.")
        except ValueError:
            raise ValueError(f"Config key '{key}' must be a valid date in the format YYYY-MM-DD. Found: '{value}'")
        
        if min_date:
            min_date_obj = datetime.strptime(min_date, "%Y-%m-%d").date()
            if value_date < min_date_obj:
                raise ValueError(f"Config key '{key}' must be on or after {min_date}. Found: {value_date}")

    @staticmethod
    def validate_string_in_list(key: str, value: Union[str, List[str]], target_list: List[str]) -> None:
        """Validate that the string or list of strings is in the target list."""
        if isinstance(value, str):
            value = [value]
        elif not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"Config key '{key}' must be a string or a list of strings. Found: '{value}'")
        
        for item in value:
            if item not in target_list:
                raise ValueError(f"Config key '{key}' contains an invalid value '{item}'. Allowed values are: {target_list}")

    @staticmethod
    def validate_is_existing_path(key: str, value: str) -> None:
        """Validate that the string represents an existing path."""
        path = Path(value)
        if not path.exists():
            raise ValueError(f"Config key '{key}' must be an existing path. Provided path '{value}' does not exist.")


    @staticmethod
    def validate_str_is_valid_path(key: str, value: str) -> None:
        """Validate that the string is a valid path format (relative or absolute)."""
        try:
            path = Path(value)
            # Check if the string is a valid path by creating a Path object
            if not isinstance(value, str) or not path:
                raise ValueError(f"Config key '{key}' must be a valid path string. Found: '{value}'")
        except Exception as e:
            raise ValueError(f"Config key '{key}' must be a valid path string. Error: {e}")


    @staticmethod
    def validate_option(key: str, value: str, allowed_values: List[str]) -> None:
        """Validate that the value is one of the allowed options."""
        if value not in allowed_values:
            raise ValueError(f"Config key '{key}' contains an invalid value '{value}'. Allowed values are: {allowed_values}")


    @staticmethod
    def validate_int_list(key: str, value: Any) -> None:
        """Validate that the value is a list of integers and print non-integer items."""
        if not isinstance(value, list):
            raise ValueError(f"Config key '{key}' must be a list. Found: {type(value).__name__}")
        
        non_int_items = [item for item in value if not isinstance(item, int)]
        
        if non_int_items:
            raise ValueError(f"Config key '{key}' must contain only integers. Found non-integer items: {non_int_items}")


    @staticmethod
    def validate_int_list_digits(key: str, value: Any, digits: int) -> None:
        """Validate that each item in the list has the specified number of digits."""
        if not isinstance(value, list):
            raise ValueError(f"Config key '{key}' must be a list. Found: {type(value).__name__}")
        
        non_matching_digits = [
            item for item in value 
            if not isinstance(item, (int, str)) or len(str(abs(int(item)))) != digits
        ]

        if non_matching_digits:
            raise ValueError(f"Config key '{key}' must contain items with exactly {digits} digits. "
                            f"Found items not matching: {non_matching_digits}")
