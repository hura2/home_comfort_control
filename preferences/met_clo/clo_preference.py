# ファイル名: clo_preference.py

from datetime import time

from pydantic import BaseModel, Field, field_validator

from translations.translated_pydantic_value_error import TranslatedPydanticValueError


class CloPreference(BaseModel):
    """衣服熱抵抗設定を管理するクラス"""

    daytime: float = Field(..., ge=0, le=3, description="日中の衣服熱抵抗（0から3の範囲）")
    """日中の衣服熱抵抗"""

    bedtime: float = Field(..., ge=0, le=3, description="就寝時の衣服熱抵抗（0から3の範囲）")
    """就寝時の衣服熱抵抗"""
