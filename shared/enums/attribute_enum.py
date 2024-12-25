from enum import Enum
from typing import Type, TypeVar

# 型パラメータの定義
T = TypeVar("T", bound="AttributesEnum")


class AttributesEnum(Enum):
    """
    `AttributesEnum`を継承することで、idやlabelをキーにしてEnumのメンバーを取得したり、
    メンバーの属性に直接アクセスできる機能を提供する基底クラス。
    """

    @classmethod
    def get_by_id(cls: Type[T], id: int) -> T:
        """
        指定されたidから対応するAttributesEnumのメンバーを返す。
        見つからない場合はNoneを返す。
        """
        for member in cls:
            if member.value.id == id:
                return member
        raise KeyError

    @classmethod
    def get_by_label(cls: Type[T], label: str) -> T:
        """
        指定されたラベルから対応するAttributesEnumのメンバーを返す。
        """
        for member in cls:
            if member.value.label == label:
                return member
        raise KeyError

    @property
    def id(self):
        return self.value.id

    @property
    def label(self):
        return self.value.label
