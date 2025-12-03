from typing import Optional, List

from pydantic import Field

from common.models._custom_base_model import CustomBaseModel
from common.models.task._contact_info_model import ContactInfo
from common.models.task._passenger_info_model import PassengerInfoModel
from common.models.task._register_info_model import RegisterModel
from common.models.task._register_segment_info_model import RegisterSegmentInfoModel


class RequestRegisterFlightModel(CustomBaseModel):
    session_id: str = Field(..., description='sessionId', alias='sessionId')
    office: str = Field(..., description='主Office', alias='office')
    data_source: str = Field(..., description='数据来源', alias='dataSource')
    connect_office: str = Field(..., description='子office', alias='connectOffice')
    register_info: Optional[RegisterModel] = Field(None, description='注册信息', alias='registerInfo')
    account_info: Optional[RegisterModel] = Field(None, description='账号信息', alias='accountInfo')
    segment_list: Optional[List[RegisterSegmentInfoModel]] = Field([], description='航段信息', alias='segmentList')
    passager_info: Optional[PassengerInfoModel] = Field(..., description='乘机人信息', alias='passagerInfo')
    contact_info: Optional[ContactInfo] = Field({}, description='联系人信息', alias='contactInfo')
    ext: Optional[dict] = Field({}, description='扩展', alias='ext')
