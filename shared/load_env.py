"""Load .env from repo root regardless of where script is run from."""
import os, sys

def load_env():
    # Walk up from current dir to find .env
    path = os.path.abspath(".")
    for _ in range(5):
        env_path = os.path.join(path, ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ.setdefault(key.strip(), val.strip())
            return True
        path = os.path.dirname(path)
    return False

load_env()
