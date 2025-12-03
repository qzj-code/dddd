"""
Module: _segment_model
Author: Ciwei
Date: 2024-09-11

Description:
    This module provides functionalities for ...
"""
from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field, field_serializer

from common.enums import SegmentTypeEnum, VoyageTypeEnum, CabinLevelEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.task._baggage_info_model import BaggageInfoModel


class SegmentInfoModel(CustomBaseModel):
    dep_airport: str = Field(..., description='出发机场', alias='depAirport')
    arr_airport: str = Field(..., description='到达机场', alias='arrAirport')
    dep_terminal: Optional[str] = Field(None, description="出发航站楼", alias='depTerminal')
    arr_terminal: Optional[str] = Field(None, description="到达航站楼", alias='arrTerminal')
    dep_time: datetime = Field(..., description='出发时间', alias='depTime')
    arr_time: datetime = Field(..., description='到达时间', alias='arrTime')
    cabin_level: CabinLevelEnum = Field(..., description='舱位等级', alias='cabinLevel')
    cabin: str = Field(..., description='舱位', alias='cabin')
    carrier: str = Field(..., description='航司', alias='carrier')
    flight_number: str = Field(..., description='航班号', alias='flightNumber')
    code_share: bool = Field(..., description='是否共享航班', alias='codeShare')
    operating_carrier: Optional[str] = Field(None, description='承运航司', alias='operatingCarrier')
    operating_flight_number: Optional[str] = Field(None, description='承运航班号', alias='operatingFlightNumber')
    aircraft: Optional[str] = Field(None, description='机型', alias='aircraft')
    distance: Optional[int] = Field(None, description='', alias='distance')
    fare_basis: Optional[str] = Field(None, description='运价基础', alias='fareBasis')
    flight_time: Optional[int] = Field(None, description='航班飞行时间', alias='flightTime')
    seat_num: Optional[int] = Field(None, description="余座", alias='seatNum')
    segment_index: int = Field(0, description='航段序号，从0开始', alias='segmentIndex')
    segment_type: SegmentTypeEnum = Field(..., description='航段类型，1:去程航段；2:回程航段', alias='segmentType')
    stop_airport: Optional[str] = Field(None, description='经停机场', alias='stopAirport')
    voyage_type: Optional[VoyageTypeEnum] = Field(None, description="航段类型", alias='voyageType')
    baggage_info: Optional[str] = Field(default=None, description="", alias='baggageInfo')
    baggage_list: List[BaggageInfoModel] = Field([], description="行李列表", alias='baggageList')

    @field_serializer('dep_time', 'arr_time', when_used='json')
    def time_serializer(self, v):
        return v.strftime('%Y%m%d%H%M')
