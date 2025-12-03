from typing import Optional

from pydantic import Field

from common.models._custom_base_model import CustomBaseModel


class RequestExChangeRateInfoModel(CustomBaseModel):
    sid: Optional[str] = Field(None, description='请求标识', alias='sid')
    from_currency: Optional[str] = Field(None, description='交易币种', alias='fromCurrency')
    to_currency: Optional[str] = Field(None, description='结算币种', alias='toCurrency')
    ext: Optional[dict] = Field(None, description='扩展参数', alias='ext')
