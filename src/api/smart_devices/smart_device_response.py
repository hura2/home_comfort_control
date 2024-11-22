from typing import Optional


class SmartDeviceResponse:
    def __init__(self, success: bool = True, message: Optional[str] = None):
        """
        デバイス操作の結果を表すレスポンスクラス

        :param success: 操作が成功したかどうか
        :param message: 成功時に返されるメッセージ
        """
        self._success = success
        self._message = message

    def __str__(self):
        return f"success:{self._success}, message:{self._message}"

    @property
    def success(self) -> bool:
        """成功かどうかを確認"""
        return self._success

    @property
    def error(self) -> bool:
        """エラーかどうかを確認"""
        return not self._success

    @property
    def message(self) -> Optional[str]:
        """成功時のデータを取得"""
        return self._message
