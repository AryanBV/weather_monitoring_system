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
        elif not config.get('api_key'):
            logger.warning("API key not found in environment variables. Some features may not work.")
            # Raise error only if we're not in a testing environment
            if os.environ.get('TESTING') != 'true':
                raise ValueError("API key not found. Set OPENWEATHERMAP_API_KEY environment variable.")

        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise