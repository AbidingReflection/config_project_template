import sys
from pathlib import Path
import pytest
import yaml
from config_tools.config_loader import ConfigLoader

# Add the root directory to the Python path (ensure it points to the parent of config_tools_module)
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

@pytest.fixture
def create_temp_yaml_file(tmp_path):
    """Fixture to create a temporary YAML file and return its path."""
    def _create_temp_yaml(content, filename="test_config.yaml"):
        # Create the temporary YAML file with the provided content
        yaml_file = tmp_path / filename
        with open(yaml_file, 'w') as f:
            yaml.dump(content, f)
        return yaml_file

    return _create_temp_yaml

@pytest.fixture
def config_loader(create_temp_yaml_file):
    """Fixture to create a ConfigLoader instance using a temporary YAML file."""
    def _create_config_loader(yaml_content, auth_yaml_content=None, config_rules=None, auth_rules=None):
        # Create the main config YAML file
        yaml_file = create_temp_yaml_file(yaml_content)

        # If there's an authentication_path, create the corresponding auth YAML file
        if auth_yaml_content:
            auth_file = create_temp_yaml_file(auth_yaml_content, filename="auth_config.yaml")
            # Update the main config to include the path to the temp auth file
            yaml_content["authentication_path"] = str(auth_file)
            yaml_file = create_temp_yaml_file(yaml_content)

        # Create the ConfigLoader instance with the updated config
        return ConfigLoader(config_path=yaml_file, config_rules=config_rules, auth_rules=auth_rules)
    
    return _create_config_loader
