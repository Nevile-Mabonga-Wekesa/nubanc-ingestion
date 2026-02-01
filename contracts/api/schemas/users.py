from pydantic import BaseModel

class UserActivateRequest(BaseModel):
    activation_token: str
