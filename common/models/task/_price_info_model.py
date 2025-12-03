"""
Module: _price_info_model
Author: Ciwei
Date: 2024-10-06

Description: 
    This module provides functionalities for ...
"""

from decimal import Decimal
from typing import Optional

from pydantic import Field, field_serializer, field_validator

from common.enums import PassengerTypeEnum
from common.models._custom_base_model import CustomBaseModel


class PriceInfoModel(CustomBaseModel):
    passenger_type: PassengerTypeEnum = Field(..., description='乘客类型', alias="passengerType")
    fare: Decimal = Field(..., description='票面', alias="fare")
    tax: Decimal = Field(..., description='税费', alias="tax")
    ext: dict = Field({}, description='扩展', alias="ext")
    integral: Optional[Decimal] = Field(0, description='积分', alias="integral")

    @field_validator('fare', 'tax', "integral", mode='before')
    def decimal_validator(cls, v: Decimal) -> Decimal:
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        v = v.quantize(Decimal('0.00'))
        return v

    @field_serializer('fare', 'tax', when_used='json')
    def decimal_serializer(self, v):
        return self.convert_data_serializer_json(v)

    @field_serializer('passenger_type', when_used='json')
    def passenger_serializer(self, v: PassengerTypeEnum) -> str:
        return v.name
