from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field

from common.models import CustomBaseModel


class CardInfo(CustomBaseModel):
    card_label: str = Field(..., alias="cardLabel", description="卡组织名称，如 VISA、MASTERCARD")
    card_type: str = Field(..., alias="cardType", description="卡类型标识")
    card_product: str = Field(..., alias="cardProduct", description="卡产品代码")
    currency: str = Field(..., description="币种")
    trans_id: str = Field(..., alias="transId", description="交易ID")
    message_digest: Optional[str] = Field("", alias="messageDigest", description="消息摘要")
    card_first_name: str = Field('', alias="cardFirstName", description="持卡人名")
    card_last_name: str = Field('', alias="cardLastName", description="持卡人姓")
    card_bin: Optional[str] = Field('', alias="cardBin", description="卡BIN")

    def get_name(self):
        return self.card_first_name + " " + self.card_last_name


class AmountInfo(CustomBaseModel):
    amount: Decimal = Field(..., description="交易金额")
    min_auth_amount: Decimal = Field(..., alias="minAuthAmount", description="最小授权金额")
    max_auth_amount: Decimal = Field(..., alias="maxAuthAmount", description="最大授权金额")


class LimitInfo(CustomBaseModel):
    active_date: datetime = Field(..., alias="activeDate", description="生效日期")
    inactive_date: datetime = Field(..., alias="inactiveDate", description="失效日期")
    auth_times: int = Field(..., alias="authTimes", description="可授权次数")
    mcc_group: str = Field(..., alias="mccGroup", description="商户类别组")


class RequestCreateCardInfoModel(CustomBaseModel):
    suplier_id: str = Field(..., alias="suplierId", description="供应商ID")
    order_no: str = Field("", alias="orderNo", description="订单号")
    card_info: CardInfo = Field(..., alias="cardInfo", description="卡信息")
    supplier_customer_id: str = Field(..., alias="supplierCustomerId", description="VCC供应商提供的客户标识")
    amount_info: AmountInfo = Field(..., alias="amountInfo", description="金额信息")
    limit_info: LimitInfo = Field(..., alias="limitInfo", description="限额信息")
