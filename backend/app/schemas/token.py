from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: str | None = None
    exp: int | None = None


class TokenData(BaseModel):
    """Token data schema for internal use."""
    email: str | None = None
