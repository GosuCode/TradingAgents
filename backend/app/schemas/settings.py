from pydantic import BaseModel


class SettingsResponse(BaseModel):
    llm_provider: str
    deep_think_llm: str
    quick_think_llm: str
    data_vendor: str
    openrouter_api_key_set: bool
    deepseek_api_key_set: bool
    openai_api_key_set: bool
    google_api_key_set: bool
    anthropic_api_key_set: bool


class SettingsUpdate(BaseModel):
    llm_provider: str | None = None
    deep_think_llm: str | None = None
    quick_think_llm: str | None = None
    data_vendor: str | None = None
    openrouter_api_key: str | None = None
    deepseek_api_key: str | None = None
    openai_api_key: str | None = None
    google_api_key: str | None = None
    anthropic_api_key: str | None = None
