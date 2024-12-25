from pathlib import Path
from typing import Any

import yaml


class YamlLoader:
    """YAMLファイルを読み込むクラス"""

    @staticmethod
    def load_config(file_name: str) -> Any:
        file_path = Path(__file__).resolve().parent.parent / "yaml" / file_name
        # YAMLファイルを読み込み、設定を返す
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
