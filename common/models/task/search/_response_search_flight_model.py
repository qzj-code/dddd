"""
Module: _response_search_flight_model
Author: Ciwei
Date: 2024-10-11

Description: 
    This module provides functionalities for ...
"""
from typing import List

from pydantic import Field

from common.models.task._fare_info_model import FareInfoModel

from common.models._custom_base_model import CustomBaseModel


class ResponseSearchFlightModel(CustomBaseModel):
    sign: str = Field(..., description='sign', alias='sign')
    session_id: str = Field(..., description='请求标识', alias='sessionId')
    fareList: List[FareInfoModel] = Field(..., alias='fareList')
