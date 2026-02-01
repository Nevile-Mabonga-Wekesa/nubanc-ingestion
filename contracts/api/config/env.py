import os

def require_env() -> str:
    if "NUBANC_ENV" not in os.environ:
        raise RuntimeError("NUBANC_ENV is required")
    return os.environ["NUBANC_ENV"]
