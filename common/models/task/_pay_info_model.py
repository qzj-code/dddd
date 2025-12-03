"""
Module: result_info_model
Author: likanghui
Date: 2024-10-15

Description:
    返回采购单支付信息模型
"""
from datetime import datetime
from typing import Optional

from pydantic import Field, field_serializer

from common.enums import PayTypeEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.task._vcc_info_model import VccInfoModel


class PayInfoModel(CustomBaseModel):
    pay_type: PayTypeEnum = Field(..., description='支付方式', alias='payType')
    vcc_info: Optional[VccInfoModel] = Field(None, description='vcc信息', alias='vccInfo')
    pay_time: datetime = Field('', description='支付时间', alias='payTime')
    serial_number: str = Field('', description='流水号', alias='serialNumber')

    @field_serializer('pay_time', when_used='json')
    def time_serializer(self, v):
        if v is None:
            return ''
        return v.strftime('%Y-%m-%d %H:%M:%S')
