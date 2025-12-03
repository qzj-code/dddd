from datetime import datetime
from typing import Optional

from pydantic import Field

from common.models import CustomBaseModel


class RequestDeleteCardInfoModel(CustomBaseModel):
    supplier_customer_id: str = Field(..., alias="supplierCustomerId", description="支付供应商唯一标识ID")
    card_id: str = Field(..., alias="cardId", description="卡ID")
