from typing import Optional


class SmartDeviceException(Exception):
    """
    スマートデバイス操作に関連する例外クラス

    Attributes:
        message (str): エラーメッセージ
        device (str): デバイス
    """

    def __init__(self, message: str, send_command: Optional[str]= None, device: Optional[str]= None):
        """
        コンストラクタ

        Args:
            message (str): エラーメッセージ
            send_command (Optional[str]): コマンド（デフォルトは None）
            device (Optional[str]): デバイス（デフォルトは None）
        """
        super().__init__(message)
        self.message = message
        self.send_command = send_command
        self.device = device

    def __str__(self) -> str:
        """
        例外メッセージの文字列表現

        Returns:
            str: エラーメッセージ、エラーコード、詳細情報を含む文字列
        """
        base_message = f"SmartDeviceException: {self.message}"
        if self.send_command:
            base_message += f" (Send Command: {self.send_command})"
        if self.device:
            base_message += f" (Device: {self.device})"
        return base_message
