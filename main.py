from modules.config_tools.config_loader import ConfigLoader
from modules.config_tools.utils import  CustomJSONEncoder
import json

from modules.config_tools.validation.validation_rules_config import config_rules
from modules.config_tools.validation.validation_rules_auth import auth_rules

CONFIG = ConfigLoader(r"configs\example.yaml", config_rules, auth_rules).get_config()

# print("Loaded config:\n", json.dumps(CONFIG, indent=4, cls=CustomJSONEncoder))