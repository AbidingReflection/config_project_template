from modules.config_tools.config_validator import ConfigValidator

config_rules = {
    'authentication_path': {
        'required': True
    },
    'qTest_domain': {
        'required': True,
        'validator': ConfigValidator.validate_https_url
    },
    'retry_attempts': {
        'required': False,
        'validator': lambda key, value: ConfigValidator.validate_int_range(key, value, min_value=0)
    },
    'log_name_prefix': {
        'required': False,
        'validator': ConfigValidator.validate_log_prefix
    },
    'max_concurrent_requests': {
        'required': True,
        'validator': lambda key, value: ConfigValidator.validate_int_range(key, value, min_value=1)
    },
}
