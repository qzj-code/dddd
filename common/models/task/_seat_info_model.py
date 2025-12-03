"""
Module: _seat_info_model
Author: Ciwei
Date: 2024-11-06

Description: 
    This module provides functionalities for ...
"""
from typing import Optional

from pydantic import Field

from common.models._custom_base_model import CustomBaseModel


class SeatInfoModel(CustomBaseModel):
    seat_code: Optional[str] = Field(None, alias='seatCode')
    seat_row: Optional[str] = Field(None, alias='seatRow')
    flight_number: Optional[str] = Field(None, alias='flightNumber')
