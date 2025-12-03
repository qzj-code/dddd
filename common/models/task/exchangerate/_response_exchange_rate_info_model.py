from pydantic import Field
from typing import Optional
from common.models._custom_base_model import CustomBaseModel
from datetime import datetime
class ResponseExChangeRateInfoModel(CustomBaseModel):
    from_currency: str = Field(..., description='交易币种', alias='fromCurrency')
    to_currency: str = Field(..., description='结算币种', alias='toCurrency')
    rate: str = Field(..., description='汇率', alias='rate')
    date: datetime = Field(..., description='采集时间', alias='date')
    bank_fee: Optional[int] = Field(None, description='服务费', alias='bankFee')