import inspect
from typing import Type

from util.string_helper import StringHelper


class TranslatedPydanticValueError(ValueError):
    def __init__(
        self,
        cls: Type | None = None,
        **kwargs,
    ):
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
        self._message_key = f"{StringHelper.camel_to_snake(class_name)}.{method_name}"
        self._context = kwargs
        super().__init__("translated_value_error")

    @property
    def message_key(self):
        return self._message_key

    @property
    def context(self):
        return self._context
