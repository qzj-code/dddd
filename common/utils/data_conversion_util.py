"""
Module: data_conversion
Author: Ciwei
Date: 2024-09-11

Description: 
    数据转换类
"""
from datetime import datetime
from enum import EnumMeta, Enum

from common.utils._date_util import DateUtil
from common.utils._enums_util import EnumsUtil


class DataConversionUtil:

    @staticmethod
    def value_to_enum(enum: EnumMeta, value: any) -> Enum:
        """
            值转enum类型
        Args:
            enum:
            value:

        Returns: enum值对象

        Raises:
            ValueError: value不存在enum对象中抛出
        """

        if value in enum:
            return value

        enum_object = EnumsUtil.value_to_enum(enum, value)
        if enum_object is None:
            raise ValueError(f'{enum.__class__.__name__} type {value} does not exist')

        return enum_object

    @staticmethod
    def string_to_datetime(value: str) -> datetime:
        """
            时间字符串转datetime
        Args:
            value:
            format_text:

        Returns:

        """

        datetime_obj = DateUtil.string_to_date_auto(value)
        if datetime_obj is None:
            raise ValueError(f'${value} is not a valid datetime')
        return datetime_obj
