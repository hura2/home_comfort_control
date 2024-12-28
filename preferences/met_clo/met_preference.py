from datetime import time

from pydantic import BaseModel, Field, ValidationError, field_validator

from translations.translated_pydantic_value_error import TranslatedPydanticValueError


class MetPreference(BaseModel):
    """代謝量設定を管理するクラス"""

    awake: float = Field(..., ge=0.5, le=2, description="日中の代謝量（0から3の範囲）")
    """日中の代謝量"""

    sleeping: float = Field(..., ge=0.5, le=2, description="就寝時の代謝量（0から3の範囲）")
    """就寝時の代謝量"""
