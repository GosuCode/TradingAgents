import os

from fastapi import APIRouter

from backend.app.schemas.settings import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["Settings"])

ENV_KEYS = {
    "openrouter_api_key": "OPENROUTER_API_KEY",
    "deepseek_api_key": "DEEPSEEK_API_KEY",
    "openai_api_key": "OPENAI_API_KEY",
    "google_api_key": "GOOGLE_API_KEY",
    "anthropic_api_key": "ANTHROPIC_API_KEY",
}

LLM_PROVIDER_CHOICES = [
    "openrouter", "deepseek", "openai", "google", "anthropic",
]


@router.get("")
def get_settings() -> SettingsResponse:
    return SettingsResponse(
        llm_provider=os.getenv("LLM_PROVIDER", "openrouter"),
        deep_think_llm=os.getenv("DEEP_THINK_LLM", "deepseek-chat"),
        quick_think_llm=os.getenv("QUICK_THINK_LLM", "deepseek-chat"),
        data_vendor=os.getenv("DATA_VENDOR", "nepse"),
        openrouter_api_key_set=bool(os.getenv("OPENROUTER_API_KEY")),
        deepseek_api_key_set=bool(os.getenv("DEEPSEEK_API_KEY")),
        openai_api_key_set=bool(os.getenv("OPENAI_API_KEY")),
        google_api_key_set=bool(os.getenv("GOOGLE_API_KEY")),
        anthropic_api_key_set=bool(os.getenv("ANTHROPIC_API_KEY")),
    )


@router.put("")
def update_settings(body: SettingsUpdate) -> SettingsResponse:
    env_file = ".env"
    env_lines = []
    if os.path.exists(env_file):
        with open(env_file) as f:
            env_lines = f.readlines()

    updates = {
        "LLM_PROVIDER": body.llm_provider,
        "DEEP_THINK_LLM": body.deep_think_llm,
        "QUICK_THINK_LLM": body.quick_think_llm,
        "DATA_VENDOR": body.data_vendor,
    }
    key_updates = {
        "OPENROUTER_API_KEY": body.openrouter_api_key,
        "DEEPSEEK_API_KEY": body.deepseek_api_key,
        "OPENAI_API_KEY": body.openai_api_key,
        "GOOGLE_API_KEY": body.google_api_key,
        "ANTHROPIC_API_KEY": body.anthropic_api_key,
    }

    for key, value in {**updates, **key_updates}.items():
        if value is None:
            continue
        found = False
        for i, line in enumerate(env_lines):
            if line.startswith(f"{key}="):
                env_lines[i] = f"{key}={value}\n"
                found = True
                break
        if not found:
            env_lines.append(f"{key}={value}\n")
        os.environ[key] = value

    with open(env_file, "w") as f:
        f.writelines(env_lines)

    return get_settings()
