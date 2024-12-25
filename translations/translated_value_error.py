import inspect
import re
from typing import Type

import i18n


class TranslatedValueError(ValueError):
    """翻訳対応のValueError"""

    def __init__(
        self,
        cls: Type | None = None,
        message_key: str | None = None,
        property_name: str | None = None,
        **kwargs,
    ):
        self._property_name = property_name
        if message_key is None:
            class_name = ""
            # 呼び出し元の情報を取得
            stack = inspect.stack()[1]  # 呼び出し元のフレームを取得
            if cls is None:
                class_name = (
                    stack.frame.f_locals.get("self", None).__class__.__name__
                    if "self" in stack.frame.f_locals
                    else None
                )
            else:
                class_name = cls.__name__
            method_name = stack.function

            if class_name:
                message_key = f"{self.camel_to_snake(class_name)}.{method_name}"
            else:
                message_key = method_name  # クラスがない場合はメソッド名のみ

        # 翻訳ファイルからエラーメッセージを取得
        self.message_key = f"error.{message_key}"
        print(self.message_key)
        self.message = i18n.t(key=self.message_key, **kwargs)
        super().__init__(self.message)

    @property
    def property_name(self):
        return self._property_name

    def camel_to_snake(self, camel_case_str: str) -> str:
        """
        キャメルケースの文字列をスネークケースに変換する関数。

        Args:
            camel_case_str (str): キャメルケースの文字列

        Returns:
            str: スネークケースに変換された文字列
        """
        # 先頭の大文字を小文字にし、単語ごとにアンダースコアを挿入
        snake_case_str = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", camel_case_str).lower()
        return snake_case_str

    def __str__(self):
        return f"{self.message}"
