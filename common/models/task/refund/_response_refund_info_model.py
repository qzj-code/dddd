from common.models._custom_base_model import CustomBaseModel
from pydantic import Field
from decimal import Decimal
from typing import Optional
from common.enums import OrderStateEnum

class ResponseRefundInfoModel(CustomBaseModel):
    session_id: str = Field(..., description='请求标识', alias='sessionId')
    office: str = Field(..., description='主Office', alias='office')
    connect_office: str = Field(..., description='子office', alias='connectOffice')
    data_source: str = Field("", description='数据源', alias='dataSource')
    order_no: str = Field("", description='订单号', alias='orderNo')
    order_state: Optional[OrderStateEnum] = Field(None, description='订单状态', alias='orderState')
    pnr: str = Field("", description='pnr', alias='pnr')
    airline_pnr: str = Field("", description='航司编码', alias='airlinePnr')
    currency: str = Field("", description='币种', alias='currency')
    returned_amount: Optional[Decimal] = Field(None, description='退回总价', alias='returnedAmount')
    tracke_number: str = Field("", description='跟踪号', alias='trackeNumber')
