from datetime import datetime
from typing import Optional, List

from pydantic import Field

from common.enums import TripTypeEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.interior_service import BaggageInfoModel
from common.models.task import ExtInfoModel


class ResponseBagageSearchInfoModel(CustomBaseModel):
    sign: str = Field(None, description='sign', alias='sign')
    session_id: str = Field(..., description='session_id', alias='sessionId')
    trip_type: TripTypeEnum = Field(..., description="trip_type", alias='tripType')
    currency: str = Field(..., description="currency", alias='currency')
    data_source: str = Field(..., description="data_source", alias='dataSource')
    office: str = Field(..., description="office", alias='office')
    connect_office: str = Field(..., description="connect_office", alias='connectOffice')
    dep_date: datetime = Field(..., description="起飞时间", alias='depDate')
    ret_date: Optional[datetime] = Field(None, description="到达时间", alias='retDate')
    private_code: Optional[list] = Field([], description="优惠码", alias='privateCode')
    ticket_carrier: str = Field(..., description="开票航司", alias='ticketCarrier')
    baggage_list: List[BaggageInfoModel] = Field([], description="行李信息", alias='baggageList')
    ext: Optional[ExtInfoModel] = Field(None, description="扩展信息", alias='ext')
