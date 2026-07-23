import yaml
import os
from logger.logging import get_logger

logger = get_logger(__name__)

def load_config():
    """ Loads configuration from a YAML file. """
    config_path = os.getenv('CONFIG_PATH', default='config/config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        logger.debug(f"Configuration loaded from {config_path}: {config}")
        return config