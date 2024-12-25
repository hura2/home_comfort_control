from abc import ABC, abstractmethod

class NotifyInterface(ABC):
    @abstractmethod
    def send_message(self, message: str) -> bool:
        """送信する"""
        pass
