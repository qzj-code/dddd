"""
Module: _flight_info_model
Author: Ciwei
Date: 2024-10-06

Description: 
    This module provides functionalities for ...
"""
from datetime import datetime
from typing import List, Optional

from pydantic import Field, field_serializer

from common.models._custom_base_model import CustomBaseModel
from common.models.interior_service._bundle_info_model import BundleInfoModel
from common.models.interior_service._segment_info_model import SegmentInfoModel


class JourneyInfoModel(CustomBaseModel):
    dep_airport: str = Field(..., description='出发机场', alias='depAirport')
    arr_airport: str = Field(..., description='到达机场', alias='arrAirport')
    dep_time: datetime = Field(..., description='出发时间', alias='depTime')
    arr_time: datetime = Field(..., description='到达时间', alias='arrTime')
    key: Optional[str] = Field(None, description='key', alias='key')
    data_source: str = Field('', description="数据源", alias='dataSource')
    segment_list: List[SegmentInfoModel] = Field(..., description='航段列表', alias='segmentList')
    bundle_list: List[BundleInfoModel] = Field(..., description='', alias='bundleList')
    correlation_id: Optional[str] = Field('', description='关联id', alias='correlation_id')

    @field_serializer('dep_time', 'arr_time', when_used='json')
    def time_serializer(self, v):
        return v.strftime('%Y-%m-%d %H:%M:%S')
