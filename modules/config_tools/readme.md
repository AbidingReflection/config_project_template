# Config Tools Module

This `config_tools` module provides utilities for loading, validating, and logging configurations for Python applications. The tools are built around YAML configuration files and offer an extensible validation mechanism for handling both general configuration and authentication-related data.

## Features
- **ConfigLoader**: Load and validate configuration from YAML files.
- **ConfigValidator**: Validate configuration against predefined rules.
- **Logger Setup**: Easily configure a logger with console and file handlers.
- **SensitiveDict**: Handle sensitive data securely in logging and JSON outputs.

## Usage

### ConfigLoader

The `ConfigLoader` is designed to load a YAML configuration file, validate it against specific rules, and set up logging for the application.

```python
from modules.config_tools import ConfigLoader

# Initialize and load config
config_loader = ConfigLoader("path/to/config.yaml", "path/to/rules_dir")
config = config_loader.get_config()
```

Key methods:
- `get_config()`: Returns the loaded and validated configuration.
- `load_authentication_config()`: Load and validate an authentication YAML file.
- `validate_config()`: Validates the loaded configuration using predefined rules.

### ConfigValidator

`ConfigValidator` checks that your configuration complies with the rules defined in a separate YAML file. These rules can enforce required fields, valid ranges, or patterns for specific keys.

```python
from modules.config_tools import ConfigValidator

# Initialize validator with configuration and rules file
validator = ConfigValidator(config, "path/to/rules.yaml")
validator.validate()
```

Key methods:
- `validate()`: Validate the configuration based on the rules.
- `load_rules_from_path()`: Load validation rules from a YAML file.

### Logger Setup

`prepare_logger` sets up logging with rotating file handlers and console output.

```python
from modules.config_tools import prepare_logger

# Set up a logger
logger = prepare_logger("logs/")
logger.info("Logger initialized successfully")
```

## Utility Classes and Functions

- **SensitiveDict**: Handles sensitive data (e.g., authentication tokens) that should not be printed or logged.
- **CustomJSONEncoder**: Custom JSON encoder for logging sensitive data, dates, and custom objects.
- **normalize_key**: Utility function for normalizing configuration keys for consistency.


### Directory Structure

```
modules/
└── config_tools/
    ├── __init__.py
    ├── config_loader.py
    ├── config_validator.py
    ├── prepare_logger.py
    ├── utils.py
    └── readme.md  # (this file)
```
