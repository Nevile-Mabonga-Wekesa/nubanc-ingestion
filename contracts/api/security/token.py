from jose import jwt, JWTError

SECRET_KEY = "change-me"
ALGORITHM = "HS256"

def decode_activation_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired activation token")
