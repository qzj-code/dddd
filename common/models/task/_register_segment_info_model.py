from datetime import datetime

from pydantic import Field

from common.enums import SegmentTypeEnum
from common.models._custom_base_model import CustomBaseModel


class RegisterSegmentInfoModel(CustomBaseModel):
    dep_airport: str = Field(..., description='出发机场', alias='depAirport')
    arr_airport: str = Field(..., description='到达机场', alias='arrAirport')
    dep_time: datetime = Field(..., description='出发时间', alias='depTime')
    arr_time: datetime = Field(..., description='到达时间', alias='arrTime')
    flight_number: str = Field(..., description='航班号', alias='flightNumber')
    segment_type: SegmentTypeEnum = Field(..., description='航段类型，1:去程航段；2:回程航段', alias='segmentType')
