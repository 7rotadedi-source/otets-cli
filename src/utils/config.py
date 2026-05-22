import os

def get_limit():
    try:
        return int(os.getenv('POST_LIMIT', 5))
    except ValueError:
        return 5
