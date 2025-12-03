"""
Module: _verify_price_model
Author: Ciwei
Date: 2024-09-09

Description:
    验价价格任务模型
"""
from datetime import datetime
from typing import List, Optional

from pydantic import Field, model_validator

from common.enums import CabinLevelEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.task._segment_info_model import SegmentInfoModel
from common.models.task.search import RequestSearchFlightModel


class RequestVerifyPriceModel(RequestSearchFlightModel):
    pnr: Optional[str] = Field(None, description="pnr", alias='pnr')
    pnrInfo: Optional[str] = Field(None, description="pnrInfo", alias='pnrInfo')
    ticketCarrier: str = Field(..., description="ticketCarrier", alias='ticketCarrier')
    segment_list: List[SegmentInfoModel] = Field(..., description="segment_list", alias='segmentList')
    cabin_level: str = Field(..., description="舱位等级", alias='cabinLevel')
    # 排除
    carrier: List[str] = Field([], description="指定航司", alias="carrier", exclude=True)
    max_connection: int = Field(0, description="最大中转点数，默认0", alias="maxConnection", exclude=True)
    trans_airport: Optional[str] = Field('', description="中转机场", alias="transAirport", exclude=True)

    @model_validator(mode='before')
    def required_check(cls, value):
        required_fields = ['sessionId', 'office', 'connectOffice', 'tripType', 'origin', 'destination', 'adultNum',
                           'childNum', 'currency', 'segmentList']
        for field in required_fields:
            if field not in value:
                raise ValueError(f'{field} is required')
        return value
