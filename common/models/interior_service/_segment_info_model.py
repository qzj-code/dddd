"""
Module: _segment_info_model
Author: Ciwei
Date: 2024-10-06

Description:
    内部Segment模型
"""
from datetime import datetime
from typing import Optional, List

from pydantic import Field, BaseModel, field_serializer, field_validator

from common.enums import VoyageTypeEnum, SegmentTypeEnum, CabinLevelEnum
from common.models.task import BaggageInfoModel, SegmentInfoModel as ApiSegmentInfoModel


class SegmentInfoModel(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    dep_airport: str = Field(..., description='出发机场', alias='depAirport')
    arr_airport: str = Field(..., description='到达机场', alias='arrAirport')
    dep_terminal: Optional[str] = Field('', description="出发航站楼", alias='depTerminal')
    arr_terminal: Optional[str] = Field('', description="到达航站楼", alias='arrTerminal')
    dep_time: datetime = Field(..., description='出发时间', alias='depTime')
    arr_time: datetime = Field(..., description='到达时间', alias='arrTime')
    carrier: str = Field(..., description='航司', alias='carrier')
    flight_number: str = Field(..., description='航班号', alias='flightNumber')
    code_share: bool = Field(..., description='是否共享航班', alias='codeShare')
    operating_carrier: Optional[str] = Field(None, description='承运航司', alias='operatingCarrier')
    operating_flight_number: Optional[str] = Field(None, description='承运航班号', alias='operatingFlightNumber')
    aircraft: Optional[str] = Field(None, description='机型', alias='aircraft')
    distance: Optional[int] = Field(None, description='', alias='distance')
    fare_basis: Optional[str] = Field(None, description='运价基础', alias='fareBasis')
    flight_time: int = Field(0, description='航班飞行时间', alias='flightTime')
    stop_airport: Optional[str] = Field('', description='经停机场', alias='stopAirport')
    voyage_type: Optional[VoyageTypeEnum] = Field(None, description="航段类型", alias='voyageType')
    segment_type: SegmentTypeEnum = Field(..., description='航段类型，1:去程航段；2:回程航段', alias='segmentType')
    ext: Optional[dict] = Field({}, alias='ext')

    @field_serializer('dep_time', 'arr_time', when_used='json')
    def time_serializer(self, v):
        return v.strftime('%Y%m%d%H%M')

    @field_validator('flight_number', 'operating_flight_number', mode='before')
    def flight_number_serializer(cls, v):
        if not v:
            return v
        return v[:2] + v[2:].zfill(4)

    def to_api_segment_model(self,
                             cabin_level: CabinLevelEnum = CabinLevelEnum.ECONOMY,
                             cabin: str = '',
                             baggage_info: str = '',
                             baggage_list: List[BaggageInfoModel] = None,
                             segment_index: int = -1,
                             seat_num: int = None):
        """
            转为接口航段模型
        Returns:


        """

        if baggage_list is None:
            baggage_list = []

        return ApiSegmentInfoModel.model_validate({
            'depAirport': self.dep_airport,
            'arrAirport': self.arr_airport,
            'depTerminal': self.dep_terminal,
            'arrTerminal': self.arr_terminal,
            'depTime': self.dep_time,
            'arrTime': self.arr_time,
            'cabinLevel': cabin_level,
            'cabin': cabin,
            'carrier': self.carrier,
            'flightNumber': self.flight_number,
            'codeShare': self.code_share,
            'operatingCarrier': self.operating_carrier,
            'operatingFlightNumber': self.operating_flight_number,
            'aircraft': self.aircraft,
            'distance': self.distance,
            'fareBasis': self.fare_basis,
            'flightTime': self.flight_time,
            'seatNum': seat_num,
            'segmentIndex': segment_index,
            'segmentType': self.segment_type,
            'stopAirport': self.stop_airport,
            'voyageType': self.voyage_type,
            'baggageInfo': baggage_info,
            'baggageList': baggage_list,
        })
