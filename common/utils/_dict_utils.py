from typing import Dict, Any
from urllib.parse import urlencode


class DictUtils:
    @staticmethod
    def urlencode_flat_dict(dictionary: Dict[str, Any]) -> str:
        """
        将包含列表值的字典进行扁平化处理，并生成 URL 编码字符串。

        Args:
            dictionary: 原始字典，支持值为 list 或 str/int 类型。

        Returns:
            str: URL 编码后的字符串（例如：a=1&a=2&b=3）
        """
        flat_data = []
        for k, v in dictionary.items():
            if v is None:
                continue  # 忽略 None 值
            if isinstance(v, list):
                # 多个值同一个键，例如：a=1&a=2
                flat_data.extend((k, str(item)) for item in v)
            else:
                flat_data.append((k, str(v)))

        return urlencode(flat_data)
