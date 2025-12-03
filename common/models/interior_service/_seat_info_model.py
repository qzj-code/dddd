"""
Module: _seat_info_model
Author: Ciwei
Date: 2024-10-19

Description:
    座位信息模型
"""
from decimal import Decimal
from typing import Optional

from pydantic import Field, field_validator

from common.models._custom_base_model import CustomBaseModel


class SeatInfoModel(CustomBaseModel):
    column: Optional[str] = Field(None, description='座位代码 如套餐包含设None', alias='column')
    row: int = Field(-1, description='行数 如套餐包含设 -1', alias='row')
    amount: Decimal = Field(Decimal(0), alias='amount')
    flight_number: Optional[str] = Field(None, alias='flightNumber')
    sell_key: Optional[str] = Field(None, alias='sellKey')

    @field_validator('flight_number', mode='before')
    def flight_number_serializer(cls, v):
        if not v:
            return v
        return v[:2] + v[2:].zfill(4)
