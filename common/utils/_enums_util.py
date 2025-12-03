"""
Module: _enums_util
Author: Ciwei
Date: 2024-09-11

Description: 
    枚举工具类
"""

from enum import EnumMeta


class EnumsUtil:

    @staticmethod
    def value_to_enum(enum: EnumMeta, value: any):
        """
            枚举成员值转枚举对象
        Args:
            enum: 枚举的原对象
            value: 枚举对象的值

        Returns: 枚举成员值,如果没有对应成员返回None

        """
        return_enum = next((x for x in enum if x.value == value), None)
        return return_enum
