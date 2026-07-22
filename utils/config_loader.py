import yaml
import os


def load_config():
    """ Loads configuration from a YAML file. """
    config_path = os.getenv('CONFIG_PATH', default='config/config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        print(f"Configuration loaded from {config_path}: {config}")
        return config