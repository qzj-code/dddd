from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field
from typing import Optional

from common.models import CustomBaseModel


class ResponseCardAuthorizationInfoModel(CustomBaseModel):
    card_log_id: str = Field(None, alias="cardLogId", description="日志唯一ID")
    request_id: str = Field(..., alias="requestId", description="请求ID")
    transaction_id: str = Field(..., alias="transactionId", description="交易ID")
    order_no: str = Field(..., alias="orderNo", description="订单号，可为空字符串")
    transaction_currency_code: str = Field(..., alias="transactionCurrencyCode", description="交易货币代码（三位 ISO 数字）")
    transaction_amount: float = Field(..., alias="transactionAmount", description="交易金额（原币种）")
    card_currency_code: str = Field(..., alias="cardCurrencyCode", description="卡币种代码")
    card_transaction_amount: float = Field(..., alias="cardTransactionAmount", description="按卡币种折算后的金额")
    response_code: str = Field(..., alias="responseCode", description="响应码")
    response_description: str = Field(..., alias="responseDescription", description="响应描述")
    approval_code: str = Field(..., alias="approvalCode", description="授权码")
    transaction_code: str = Field(..., alias="transactionCode", description="交易类型代码")
    transaction_date: str = Field(..., alias="transactionDate", description="交易时间 YYYY-MM-DD HH:MM:SS")
    local_time: Optional[str] = Field(None, alias="localTime", description="本地时间，可为 null")
    merchant_name: str = Field(..., alias="merchantName", description="商户名称")
    mcc: str = Field(..., alias="mcc", description="商户类别码")
    merchant_country: str = Field(..., alias="merchantCountry", description="商户国家")
    merchant_city: str = Field(..., alias="merchantCity", description="商户城市")
    merchant_id: str = Field(..., alias="merchantId", description="商户ID")
    acquiring_bank_id: str = Field(..., alias="acquiringBankId", description="收单行ID")
    credit_transaction_sign: str = Field(..., alias="creditTransactionSign", description="正负交易标识")
    reversal_type: str = Field(..., alias="reversalType", description="冲正类型")
