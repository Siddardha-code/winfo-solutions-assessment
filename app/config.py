import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    aws_region: str
    model_id: str
    llm_mode: str  # "bedrock" | "mock"
    api_key: str | None
    max_tokens: int


@lru_cache
def get_settings() -> Settings:
    return Settings(
        aws_region=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0"),
        llm_mode=os.getenv("LLM_MODE", "bedrock"),
        api_key=os.getenv("API_KEY") or None,
        max_tokens=int(os.getenv("MAX_TOKENS", "700")),
    )
