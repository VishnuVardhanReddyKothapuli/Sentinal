from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Registration(BaseModel):
    model_config = ConfigDict(extra='forbid')
    username: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_.-]+$')
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=12, max_length=128)

    @field_validator('username', 'email')
    @classmethod
    def normalize(cls, value: str) -> str:
        return value.lower()


class Login(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=128)


class PurgeRequest(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=100)
