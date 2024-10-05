from  modules.config_tools.config_validator import ConfigValidator

auth_rules  = {
    'qTest_bearer_token': {
        'required': True,
        'validator': ConfigValidator.validate_qTest_bearer_token
    }
}
