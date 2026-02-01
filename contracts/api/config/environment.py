import os

ALLOWED_ENVS = {"dev", "staging", "prod"}

def get_env() -> str:
    env = os.environ.get("NUBANC_ENV")

    if not env:
        raise RuntimeError("NUBANC_ENV is not set")

    if env not in ALLOWED_ENVS:
        raise RuntimeError(f"Invalid NUBANC_ENV: {env}")

    return env
