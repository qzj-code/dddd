from typing import Optional, List

from pydantic import Field

from common.enums import OrderStateEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.task import PriceInfoModel, PayInfoModel, ExtInfoModel


class ResponsePayInfoModel(CustomBaseModel):
    office: str = Field(..., description='主Office', alias='office')
    connect_office: str = Field(..., description='子office', alias='connectOffice')
    order_no: str = Field("", description='订单号', alias='orderNo')
    order_state: Optional[OrderStateEnum] = Field(None, description='订单状态', alias='orderState')
    pnr: str = Field("", description='pnr', alias='pnr')
    airline_pnr: str = Field("", description='航司编码', alias='airlinePnr')
    currency: str = Field("", description='币种', alias='currency')
    price_list: Optional[List[PriceInfoModel]] = Field([], description='价格信息', alias='priceList')
    pay_info: Optional[PayInfoModel] = Field(None, description='支付信息', alias='payInfo')
    ext: Optional[ExtInfoModel] = Field(None, description='扩展信息', alias='ext')
