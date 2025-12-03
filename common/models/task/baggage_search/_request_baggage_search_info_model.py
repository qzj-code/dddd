from datetime import datetime
from typing import Optional, List

from pydantic import Field

from common.enums import TripTypeEnum, CabinLevelEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.task import ExtInfoModel


class RequestBagageSearchInfoModel(CustomBaseModel):
    session_id: str = Field(..., description='sessionId', alias='sessionId')
    office: str = Field(..., description='主Office', alias='office')
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
    carrier: List[str] = Field(..., description="指定航司", alias="carrier")
    currency: str = Field(..., description="币种", alias="currency")
    flight_number: str = Field(..., description="航班号", alias="flightNumber")
    ext: Optional[ExtInfoModel] = Field(None, description="拓展字段", alias="ext")
