"""
Module: _meal_code_model
Author: Ciwei
Date: 2024-11-01

Description: 
    This module provides functionalities for ...
"""
from decimal import Decimal
from typing import Optional

from pydantic import Field

from common.models._custom_base_model import CustomBaseModel


class CateringInfoModel(CustomBaseModel):
    code: Optional[str] = Field(None, description='餐食代码 如套餐包含设None', alias='code')
    amount: Decimal = Field(Decimal(0), deprecated='费用', alias='amount')
    currency: Optional[str] = Field(None, deprecated='币种', alias='currency')
    flight_number: Optional[str] = Field(None, deprecated='航班号', alias='flightNumber')
    sell_key: Optional[str] = Field(None, alias='sellKey')
