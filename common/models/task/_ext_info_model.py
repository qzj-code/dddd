"""
Module: _ext_info_model
Author: Ciwei
Date: 2024-09-09

Description:
    扩展字段模型
"""
from decimal import Decimal
from typing import Optional, Any

from pydantic import Field

from common.models._custom_base_model import CustomBaseModel


class ExtInfoModel(CustomBaseModel):
    sid: Optional[str] = Field('', description='爬虫区分程序的id 必传', alias='sid')
    sign: Optional[str] = Field('', description='接口鉴权标识', alias='sign')
    is_async: Optional[bool] = Field(False, description='是否异步', alias='async')
    call_back_url: Optional[str] = Field('', description='回调地址', alias='callBackUrl')
    user: Optional[str] = Field('', description='用户名', alias='user')
    password: Optional[str] = Field('', description='密码', alias='password')
    task_id: Optional[str] = Field('', description='任务id', alias='taskId')
    order_detail_url: Optional[str] = Field('', description='订单详情地址', alias='orderDetailUrl')
    payment_url: Optional[str] = Field('', description='支付地址', alias='paymentUrl')
    serial_number: Optional[str] = Field('', description='流水号', alias='serialNumber')
    pay_procedure_fee: Optional[Decimal] = Field(Decimal(0), description='支付手续费', alias='payProcedureFee')
    trae_id: Optional[str] = Field('', description='订单特殊id', alias='traeId')
    payOrderId: Optional[str] = Field('', description='订单特殊id', alias='payOrderId')

    channel: Optional[Any] = Field(None, description='渠道', alias='channel')
    subChannel: Optional[Any] = Field(None, description='子渠道', alias='subChannel')
    scMarket: Optional[Any] = Field(None, description='市场', alias='scMarket')
    agencyID: Optional[Any] = Field(None, description='代理ID', alias='agencyID')