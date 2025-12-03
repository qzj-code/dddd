"""
Module: _baggage_model
Author: Ciwei
Date: 2024-09-11

Description: 
    This module provides functionalities for ...
"""
from typing import Optional

from pydantic import Field

from common.enums import BaggageTypeEnum, PassengerTypeEnum
from common.models._custom_base_model import CustomBaseModel


class BaggageInfoModel(CustomBaseModel):
    passenger_type: PassengerTypeEnum = Field(..., description="乘客类型", alias="passengerType")
    baggage_type: BaggageTypeEnum = Field(None, description="行李类型", alias="baggageType")
    pieces: int = Field(0, description="件数", alias="pieces")
    total_weight: Optional[int] = Field(0, description="重量", alias="totalWeight")
    weight_unit: str = Field("KG", description="重量单位", alias="weightUnit")
