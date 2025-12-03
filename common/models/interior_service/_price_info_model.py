"""
Module: _price_info_model
Author: Ciwei
Date: 2024-10-07

Description: 
    This module provides functionalities for ...
"""
from decimal import Decimal
from typing import Optional

from pydantic import Field, field_validator, field_serializer

from common.enums import PassengerTypeEnum
from common.models import CustomBaseModel


class PriceInfoModel(CustomBaseModel):
    currency: str = Field(..., description="", alias='currency')
    passenger_type: PassengerTypeEnum = Field(..., description='乘客类型', alias="passengerType")
    fare: Decimal = Field(..., description='票面', alias="fare")
    tax: Decimal = Field(..., description='税费', alias="tax")
    integral: Optional[Decimal] = Field(0, description='积分', alias="integral")
    ext: dict = Field({}, description='扩展', alias="ext")

    @field_validator('fare', 'tax', mode='before')
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
