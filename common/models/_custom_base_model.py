"""
Module: _base_model
Author: Ciwei
Date: 2024-09-13

Description:
    自定义基础模型，下级模型继承此模型做数据处理
"""

from datetime import datetime
from decimal import Decimal
from typing import get_origin, Union

from pydantic import BaseModel, model_validator

from common.utils.data_conversion_util import DataConversionUtil


class CustomBaseModel(BaseModel):

    @staticmethod
    def get_fields_data(fields_data, name):
        """
            查找，并获取字段数据
        Args:
            fields_data:
            name:

        Returns:

        """

        for field_name in fields_data:
            alias = fields_data[field_name].alias
            if alias is None:
                continue
            if alias == name or field_name == name:
                return fields_data[field_name]

        return None

    @classmethod
    def convert_data(cls, data_type, data_value):
        try:
            if data_type is datetime:
                if isinstance(data_value, datetime):
                    return data_value

                if not data_value:
                    return None

                if data_type:
                    return DataConversionUtil.string_to_datetime(value=data_value)
                else:
                    return None
        except TypeError as b:
            print(data_type, data_value)
            print(b)

        return data_value

    @classmethod
    def __get_union_list(cls, data):

        return get_origin(data)

    @classmethod
    def convert_data_serializer_json(cls, value):
        if isinstance(value, Decimal):
            return float(value)
        return value

    @model_validator(mode="before")
    def modify_fields(cls, values):
        """
            初始化数据处理
        Args:
            values:

        Returns:

        """

        if values is None:
            return values
        try:
            for source_fields_name, source_fields_value in values.items():
                field_info = cls.get_fields_data(cls.model_fields, source_fields_name)

                if field_info is None:
                    continue

                if field_info.annotation == datetime:
                    values[source_fields_name] = cls.convert_data(data_type=datetime, data_value=source_fields_value)

                try:
                    union_data = cls.__get_union_list(field_info.annotation)
                    if union_data == Union:
                        if not isinstance(source_fields_value, str):
                            continue

                        for union_value in field_info.annotation.__args__:
                            try:
                                values[source_fields_name] = cls.convert_data(data_type=union_value,
                                                                              data_value=source_fields_value)
                                break
                            except TypeError as b:
                                pass
                except TypeError as b:
                    pass
        except AttributeError as a:
            pass

        return values
