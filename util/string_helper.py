import re

class StringHelper:
    """
    文字列ユーティリティクラス
    """
    @staticmethod
    def camel_to_snake(camel_case_str: str | None = None) -> str:
        """
        キャメルケースの文字列をスネークケースに変換する関数。

        Args:
            camel_case_str (str): キャメルケースの文字列

        Returns:
            str: スネークケースに変換された文字列
        """
        if camel_case_str is None:
            return ""
        # 先頭の大文字を小文字にし、単語ごとにアンダースコアを挿入
        snake_case_str = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", camel_case_str).lower()
        return snake_case_str
