from datetime import datetime
from typing import Optional

from pydantic import Field

from common.models import CustomBaseModel


class RequestCardAuthorizationInfoModel(CustomBaseModel):
    supplier_customer_id: str = Field(..., alias="supplierCustomerId", description="支付供应商唯一标识ID")
    card_id: str = Field(..., alias="cardId", description="卡ID")
    transaction_start_time: Optional[datetime] = Field(None, alias="transactionStartTime", description="交易开始时间(交易时间前1小时)")
    transaction_end_time: Optional[datetime] = Field(None, alias="transactionEndTime", description="交易结束时间(交易时间后1小时)")
