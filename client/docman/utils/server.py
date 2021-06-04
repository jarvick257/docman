from .config import get_config


def get_server_url():
    config = get_config()
    return f"http://{config['SERVER']['address']}:{config['SERVER']['port']}"
