from pydantic import BaseModel, Field


class ComfortFactors(BaseModel):
    """
    MET（代謝当量）および CLO（着衣量）を保持する Pydantic モデル。

    Attributes:
        met (float): MET値。通常は1.0〜2.0程度（活動レベルに応じて異なる）。
        clo (float): CLO値。通常は0.0〜1.5程度（衣服の断熱性に基づく）。
    """

    met: float = Field(..., ge=0.6, le=3.0, description="MET値（0.6〜3.0の範囲で指定）")
    """MET値"""
    clo: float = Field(..., ge=0.0, le=3.0, description="CLO値（0.0〜3.0の範囲で指定）")
    """CLO値"""
