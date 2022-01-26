from terality._terality.utils.config import TeralityConfig, TeralityCredentials


def has_valid_terality_config_file() -> bool:
    try:
        TeralityConfig.load()
        return True
    # TODO: finer-grained exception handling
    except Exception:
        return False


def has_valid_terality_credentials_file() -> bool:
    try:
        TeralityCredentials.load()
        return True
    # TODO: finer-grained exception handling
    except Exception:
        return False
