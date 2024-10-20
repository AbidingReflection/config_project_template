from modules.config_tools.config_loader import ConfigLoader
from modules.config_tools.utils import  CustomJSONEncoder
import json

CONFIG = ConfigLoader(r"configs\example.yaml").get_config()