import os


def is_debug():
    return os.getenv("DEBUG", "false").lower() in ("true", "1")
