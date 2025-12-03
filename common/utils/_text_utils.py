"""
@Project     : flyscoot
@Author      : ciwei
@Date        : 2023/12/17 18:26
@Description :
@versions    : 1.0.0.0
"""
import random
import string
from typing import Optional


class TextUtils:

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
    def extract_all_between(cls, text, start, end):
        """
        从文本中提取所有开始和结束标识符之间的内容。

        :param text: 要从中提取内容的原始文本。
        :param start: 开始标识符。
        :param end: 结束标识符。
        :return: 所有提取内容的列表。
        """
        results = []
        start_index = 0

        while True:
            # 查找开始标识符
            start_index = text.find(start, start_index)
            if start_index == -1:
                break  # 如果没有找到开始标识符，退出循环

            # 移动到开始标识符之后
            start_index += len(start)

            # 查找结束标识符
            end_index = text.find(end, start_index)
            if end_index == -1:
                break  # 如果没有找到结束标识符，退出循环

            # 提取子串并添加到结果列表
            results.append(text[start_index:end_index])

            # 更新开始索引，继续查找下一个
            start_index = end_index + len(end)

        return results

    @classmethod
    def generate_random_string(cls, length, use_figure: Optional[bool] = False):
        """
        生成指定长度的随机字符串
        """

        # 随机生成第一个字符，不能是数字
        first_char = random.choice(string.ascii_letters)

        if use_figure:
            remaining_chars = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length - 1))
        else:
            remaining_chars = ''.join(random.choice(string.ascii_letters) for _ in range(length - 1))

        # 拼接第一个字符和剩余字符
        random_string = first_char + remaining_chars
        return random_string

    @classmethod
    def extract_until_char(cls, text, char):
        index = text.find(char)
        if index != -1:
            return text[:index]
        return None
