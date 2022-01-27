from pydantic import BaseModel, Field

class UserRegistration(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str
    api_key: str = Field(alias='key')
    organization_id: int = Field(alias='organizationId')
    class Config:
        allow_population_by_field_name = True
