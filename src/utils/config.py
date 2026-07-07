import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    llm_model: str
    llm_base_url: str | None
    debug_provider: bool


def get_settings() -> Settings:
    load_dotenv(dotenv_path=ENV_FILE, override=True)
    return Settings(
        api_key=os.getenv("OPENAI_API_KEY"),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        llm_base_url=os.getenv("LLM_BASE_URL") or None,
        debug_provider=os.getenv("DEBUG_PROVIDER", "false").lower() == "true",
    )
