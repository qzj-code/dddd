"""
Module: _string_util
Author: Ciwei
Date: 2024-09-13

Description:
    字符串工具类
"""
import random
import string


class StringUtil:
    @staticmethod
    def generate_random_string(length, use_digits=True, use_special_chars=False):
        """
            取随机长度字符串
        Args:
            length: 长度
            use_digits: 使用数字
            use_special_chars: 使用特殊字符

        Returns:

        """
        # 初始化可用字符集
        characters = ""

        # 根据参数添加不同的字符集

        characters += string.ascii_letters  # 包含大小写字母
        if use_digits:
            characters += string.digits  # 包含数字 0-9
        if use_special_chars:
            characters += string.punctuation  # 包含特殊字符，如 !, @, #

        # 生成随机字符串
        return ''.join(random.choices(characters, k=length))

    @staticmethod
    def to_pascal_case(s):
        # 替换分隔符为统一的空格
        s = s.replace('-', ' ').replace('_', ' ')

        # 分割字符串为单词列表
        words = s.split()

        # 将每个单词首字母大写，合并成 PascalCase
        pascal_case = ''.join(word.capitalize() for word in words)

        return pascal_case

    @classmethod
    def extract_last_between(cls, text: str, target_str: str):
        """

        Args:
            text:要从中提取的文本
            target_str:需要查找的目标字符串

        Returns:
            str:target_str之前的文本内容，如果未找到 target_str，则返回 None
        """
        start_index = text.find(target_str)
        if start_index == -1:
            return None

        return text[:start_index]

    @classmethod
    def extract_first_between(cls, text: str, target_str: str):
        """

        Args:
            text: 要从中提取的文本
            target_str: 需要查找的目标字符串

        Returns:

        """

        start_index = text.find(target_str)
        if start_index == -1:
            return None

        return text[start_index + len(target_str):]

    @classmethod
    def extract_between(cls, text, start, end):
        """
        从文本中提取开始和结束标识符之间的内容。

        :param text: 要从中提取内容的原始文本。
        :param start: 开始标识符。
        :param end: 结束标识符。
        :return: 开始和结束标识符之间的内容。
        """
        start_index = text.find(start)
        if start_index == -1:
            return None  # 如果未找到开始标识符，返回 None

        start_index += len(start)  # 移动到开始标识符之后
        end_index = text.find(end, start_index)
        if end_index == -1:
            return None  # 如果未找到结束标识符，返回 None

        return text[start_index:end_index]

    @classmethod
    def extract_all_between(cls,text, start_tag, end_tag):
        results = []
        start_index = 0

        while True:
            # 找到每个标签的起始位置
            start_index = text.find(start_tag, start_index)
            if start_index == -1:
                break  # 如果找不到更多的标签，退出循环

            # 找到每个标签的结束位置
            end_index = text.find(end_tag, start_index)
            if end_index == -1:
                break  # 如果没有找到结束标记，则退出循环

            # 提取 start_tag 和 end_tag 之间的内容
            content = text[start_index + len(start_tag):end_index].strip()

            # 将提取的内容添加到结果列表
            results.append(content)

            # 更新 start_index，从当前结束位置继续查找
            start_index = end_index + len(end_tag)

        return results

