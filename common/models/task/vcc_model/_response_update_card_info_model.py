from datetime import datetime

from pydantic import BaseModel, Field, field_validator, AliasChoices, ConfigDict
import re

from common.models import CustomBaseModel


class CardInfo(CustomBaseModel):

    card_id: str = Field(..., alias="cardId", description="卡片ID(vcc供应商提供的唯一值)")
    card_number: str = Field(..., alias="cardNumber", description="vcc卡号")
    expire_date: datetime = Field(..., alias="expireDate", description="有效期（时间格式）")
    cvv_dta: str = Field(..., alias='cvvDta', description="vcc安全码")


class ResponseUpdateCardInfoModel(CustomBaseModel):

    msg: str = Field(..., alias="msg", description="结果描述")
    code: str = Field(..., alias="code", description="状态码（字符串）")
    data: CardInfo = Field(..., alias="data", description="响应结果")
    success: bool = Field(..., alias="success", description="响应状态")
