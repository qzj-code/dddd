from typing import Optional

from common.enums import PayTypeEnum
from common.models._custom_base_model import CustomBaseModel
from pydantic import Field, model_validator
from decimal import Decimal
from common.models.task._vcc_info_model import VccInfoModel


class RequestPayInfoModel(CustomBaseModel):
    session_id: str = Field(..., description='请求标识', alias='sessionId')
    office: str = Field(..., description='主Office', alias='office')
    connect_office: str = Field(..., description='子office', alias='connectOffice')
    pnr: str = Field("", description='pnr', alias='pnr')
    orderNo: str = Field("", description='订单号', alias='orderNo')
    total_price: Decimal = Field("", description='订单总价', alias='totalPrice')
    pay_type: PayTypeEnum = Field(..., description='支付方式', alias='payType')
    vccpay_info: Optional[VccInfoModel] = Field([], description='vcc信息', alias='vccInfo')
    ext: dict = Field(..., description='扩展', alias='ext')

    @model_validator(mode='before')
    def required_check(cls, value):
        required_fields = ['sessionId', 'office', 'connectOffice', 'pnr', 'orderNo', 'totalPrice',
                           'payType']
        for field in required_fields:
            if field not in value:
                raise ValueError(f'{field} is required')
        return value
