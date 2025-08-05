from typing import Dict, cast

import i18n

i18n.set("file_format", "yaml")
i18n.load_path.append("./translations")
i18n.set("locale", "ja")


class WeekdayHelper:
    """
    曜日名とインデックス（0〜6）との相互変換を行うユーティリティクラス。
    設定ファイル側でバリデーションされている前提。
    """

    @staticmethod
    def _get_label_by_index(index: int) -> str | None:
        """
        指定されたインデックスの曜日ラベルをi18nから取得する。
        """
        return i18n.t(f"weekday.labels.{index}", default=None)

    @classmethod
    def label_to_index(cls, name: str) -> int | None:
        """
        曜日名（例: "月"）をインデックス（0〜6）に変換する。
        """
        for idx in range(7):
            if cls._get_label_by_index(idx) == name:
                return idx
        return None

    @classmethod
    def index_to_name(cls, index: int) -> str | None:
        """
        インデックス（0〜6）を曜日名（例: "月"）に変換する。
        """
        return cls._get_label_by_index(index)
