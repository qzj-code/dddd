"""
Module: _search_flight_model
Author: Ciwei
Date: 2024-09-09

Description:
    查询任务模型
"""

from datetime import datetime
from typing import Optional, List

from pydantic import Field, model_validator, ValidationError
from pydantic.v1.error_wrappers import ErrorWrapper

from common.enums import TripTypeEnum, CabinLevelEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.task._ext_info_model import ExtInfoModel


class RequestSearchFlightModel(CustomBaseModel):
    session_id: str = Field(..., description='sessionId', alias='sessionId')
    office: str = Field(..., description='主Office', alias='office')
    data_source: str = Field(..., description='数据来源', alias='dataSource')
    connect_office: str = Field(..., description='子office', alias='connectOffice')
    trip_type: TripTypeEnum = Field(..., description="行程类型", alias='tripType')
    origin: str = Field(..., description="出发地", alias='origin')
    destination: str = Field(..., description="目的地", alias='destination')
    dep_date: datetime = Field(..., description="出发日期", alias='depDate')
    ret_date: Optional[datetime] = Field(None, description="返程日期", alias='retDate')
    cabin_level: Optional[List[CabinLevelEnum]] = Field([], description="舱位等级", alias='cabinLevel')
    adult_number: int = Field(..., description="成人人数", alias="adultNum")
    child_number: int = Field(..., description="儿童人数", alias="childNum")
    private_code: Optional[List[str]] = Field([], description="私有运价代码", alias="privateCode")
    passenger_code: Optional[List[str]] = Field([], description="特殊乘机人代码", alias="passengerCode")
    carrier: List[str] = Field([], description="指定航司", alias="carrier")
    max_connection: int = Field(0, description="最大中转点数，默认0", alias="maxConnection")
    trans_airport: Optional[str] = Field('', description="中转机场", alias="transAirport")
    currency: str = Field(..., description="币种", alias="currency")
    ext: Optional[ExtInfoModel] = Field(ExtInfoModel(), description="拓展字段", alias="ext")

    @model_validator(mode='before')
    def required_check(cls, value):
        required_fields = ['sessionId', 'office', 'connectOffice', 'tripType', 'origin', 'destination', 'adultNum',
                           'childNum', 'currency']
        for field in required_fields:
            if field not in value:
                raise ValueError(f'{field} is required')
        return value
