from datetime import datetime

from pydantic import Field

from common.models import CustomBaseModel


class ResponseCreateCardInfoModel(CustomBaseModel):
    card_id: str = Field(..., alias="cardId", description="卡ID")
    card_number: str = Field(..., alias="cardNumber", description="卡号")
    expire_date: datetime = Field(..., alias="expireDate", description="有效期，时间格式")
    cvv_data: str = Field(..., alias="cvvData", description="CVV 安全码")
    card_type: str = Field(..., alias="cardType", description="卡类型")
    card_label: str = Field(..., alias="cardLabel", description="卡组织")