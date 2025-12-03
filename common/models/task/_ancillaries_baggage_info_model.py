"""
Module: _ancillaries_baggage_info_model
Author: Ciwei
Date: 2024-10-28

Description: 
    This module provides functionalities for ...
"""
from decimal import Decimal
from typing import Optional

from pydantic import Field, field_validator, field_serializer

from common.enums import PassengerTypeEnum, BaggageTypeEnum
from common.models._custom_base_model import CustomBaseModel


class AncillaryBaggageInfoModel(CustomBaseModel):
    passenger_type: Optional[PassengerTypeEnum] = Field(None, description="乘客类型", alias="passengerType")
    baggage_type: BaggageTypeEnum = Field(None, description="行李类型", alias="baggageType")
    pieces: int = Field(0, description="件数", alias="pieces")
    total_weight: Optional[int] = Field(None, description="重量", alias="totalWeight")
    weight_unit: str = Field("KG", description="重量单位", alias="weightUnit")
    flight_number: Optional[str] = Field("", description="航班号,中转用$拼接", alias="flightNumber")
    amount: Decimal = Field(Decimal(0), description="行李购买金额", alias="amount")

    @field_validator('flight_number', mode='before')
    def flight_number_serializer(cls, v):
        if v is None:
            return v
        flight_numbers = v.split('$')
        result_flight_number = []
        for flight_number in flight_numbers:
            result_flight_number.append(flight_number[:2] + flight_number[2:].zfill(4))

        return '$'.join(result_flight_number)

    @field_validator('amount', mode='before')
    def decimal_validator(cls, v: Decimal) -> Decimal:
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        v = v.quantize(Decimal('0.00'))
        return v

    @field_serializer('amount', when_used='json')
    def decimal_serializer(self, v):
        return self.convert_data_serializer_json(v)
