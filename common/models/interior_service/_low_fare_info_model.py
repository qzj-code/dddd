from typing import Any
from typing import Optional

from pydantic import Field

from common.models._custom_base_model import CustomBaseModel


class LowFareInfoModel(CustomBaseModel):
    productType: Optional[Any] = Field(None, description='产品类型，网站实际展示的产品类型', alias='productType')
    invoiceType: Optional[Any] = Field(None, description='报销凭证', alias='invoiceType')
    isOwn: Optional[Any] = Field(None, description='是否自营', alias='isOwn')
    showState: Optional[Any] = Field(None, description='展示状态', alias='showState')
    passengerRestriction: Optional[Any] = Field(None, description='乘机人限制', alias='passengerRestriction')

    channel: Optional[Any] = Field(None, description='渠道', alias='channel')
    subChannel: Optional[Any] = Field(None, description='子渠道', alias='subChannel')
    scMarket: Optional[Any] = Field(None, description='市场', alias='scMarket')
    agencyID: Optional[Any] = Field(None, description='代理ID', alias='agencyID')
