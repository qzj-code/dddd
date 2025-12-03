from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from common.models import CustomBaseModel


class RequestUpdateCardInfoModel(CustomBaseModel):
    supplier_customer_id: str = Field(..., alias="supplierCustomerId", description="支付供应商唯一标识ID")
    key_id: str = Field(..., alias="keyId", description="卡片主键ID")
    card_id: str = Field(..., alias="cardId", description="卡ID")
    status: str = Field(..., alias="status", description="卡状态")
    card_number: str = Field(..., alias="cardNumber", description="卡号")

    card_limit: Optional[Decimal] = Field(None, alias="cardLimit", description="额度")
    min_auth_amount: Optional[Decimal] = Field(None, alias="minAuthAmount", description="授权金额下限")
    max_auth_amount: Optional[Decimal] = Field(None, alias="maxAuthAmount", description="授权金额上限")

    active_date: Optional[date] = Field(None, alias="activeDate", description="生效日期，yyyy-MM-dd")
    inactive_date: Optional[date] = Field(None, alias="inactiveDate", description="失效日期，yyyy-MM-dd")

    mcc_group: Optional[str] = Field(None, alias="mccGroup", description="TripLink定义的MCC组名")
    order_no: Optional[str] = Field(None, alias="orderNo", description="订单号")