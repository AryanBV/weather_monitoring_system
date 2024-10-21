import yaml
import os
from src.utils.logger import logger

def load_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Override API key with environment variable if set
        api_key = os.environ.get('OPENWEATHERMAP_API_KEY')
        if api_key:
            config['api_key'] = api_key
        elif 'api_key' not in config:
            raise ValueError("API key not found in config or environment variables")

        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise