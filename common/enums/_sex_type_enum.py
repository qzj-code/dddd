"""
Module: _sex_type_enum
Author: likanghui
Date: 2024-09-11

Description:
    新别枚举
"""
from enum import Enum


class SexTypeEnum(Enum):
    F = "F"  # 女
    M = "M"  # 男

    @staticmethod
    def get_value(name):
        try:
            return SexTypeEnum[name].value
        except KeyError:
            return None

    @staticmethod
    def get_object(name):
        try:
            return SexTypeEnum[name]
        except KeyError:
            return None
