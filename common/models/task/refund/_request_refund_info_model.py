from pydantic import Field, model_validator

from common.models._custom_base_model import CustomBaseModel
from common.models.task import ContactInfo, PassengerInfoModel, SegmentInfoModel


class RequestRefundInfoModel(CustomBaseModel):
    session_id: str = Field(..., description='请求标识', alias='sessionId')
    office: str = Field(..., description='主Office', alias='office')
    connect_office: str = Field(..., description='子office', alias='connectOffice')
    data_source: str = Field("", description='数据源', alias='dataSource')
    order_no: str = Field("", description='订单号', alias='orderNo')
    refund_type: int = Field(0, description='退票类型', alias='refundType')
    pnr: str = Field("", description='pnr', alias='pnr')
    segment_list: list = Field([SegmentInfoModel], description='航班列表', alias='segmentList')
    passenger_list: list = Field([PassengerInfoModel], description='乘机人信息列表', alias='passengerList')
    contact_info: ContactInfo = Field(..., description='联系人信息', alias='contactInfo')
    ext: dict = Field(..., description='扩展', alias='ext')

    @model_validator(mode='before')
    def required_check(cls, value):
        required_fields = ['sessionId', 'office', 'connectOffice', 'pnr', 'passengerList', 'segmentList',
                           'contactInfo']
        for field in required_fields:
            if field not in value:
                raise ValueError(f'{field} is required')
        return value
