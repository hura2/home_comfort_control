class SmartHomeDeviceResponse:
    """
    デバイス操作の結果を表すレスポンスクラス。

    このクラスは、スマートホームデバイスの操作結果（成功・失敗）とその
    メッセージを管理します。デバイス操作が成功したかどうか、または失敗した場合の
    メッセージを取得することができます。

    Attributes:
        success (bool): 操作が成功したかどうかを示すフラグ。
        message (Optional[str]): 操作成功時に返されるメッセージ。
    """

    def __init__(self, success: bool = True, message: str | None = None):
        """
        SmartHomeDeviceResponseのコンストラクタ。

        デバイス操作が成功したかどうか、またその際のメッセージを指定する。

        Args:
            success (bool, optional): 操作が成功したかどうか。デフォルトはTrue。
            message (Optional[str], optional): 成功時のメッセージ。デフォルトはNone。
        """
        self._success = success
        self._message = message

    def __str__(self):
        """
        オブジェクトの文字列表現を返す。

        Returns:
            str: 成功/失敗のステータスとメッセージを示す文字列。
        """
        return f"success:{self._success}, message:{self._message}"

    @property
    def success(self) -> bool:
        """
        成功かどうかを確認するプロパティ。

        Returns:
            bool: 操作が成功した場合はTrue、それ以外はFalse。
        """
        return self._success

    @property
    def error(self) -> bool:
        """
        エラーかどうかを確認するプロパティ。

        エラーの場合はTrue、成功の場合はFalse。

        Returns:
            bool: エラーの場合はTrue、それ以外はFalse。
        """
        return not self._success

    @property
    def message(self) -> str | None:
        """
        成功時のメッセージを取得するプロパティ。

        Returns:
            Optional[str]: 操作が成功した場合のメッセージ。失敗時はNone。
        """
        return self._message
