from pydantic import BaseModel, Field, field_validator


class UserProfile(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(description="11-digit Egyptian phone number")
    age: int = Field(ge=10, le=120)
    city: str = Field(min_length=2, max_length=100)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        valid_prefix = value.startswith(("010", "011", "012", "015"))
        if len(value) != 11 or not value.isdigit() or not valid_prefix:
            raise ValueError("Phone number must be 11 digits and start with 010, 011, 012, or 015.")
        return value


class Ticket(BaseModel):
    phone: str = Field(min_length=11, max_length=11)
    issue_type: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=5, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    reply: str


class RuntimeSettingsUpdate(BaseModel):
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")
    qdrant_url: str | None = Field(default=None, alias="QDRANT_URL")
    qdrant_api_key: str | None = Field(default=None, alias="QDRANT_API_KEY")

    model_config = {"populate_by_name": True}

    def present_values(self) -> dict[str, str]:
        return {key: value for key, value in self.model_dump(by_alias=True).items() if value}
