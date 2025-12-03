"""
Module: _vcc_info_model
Author: Ciwei
Date: 2024-10-10

Description: 
    This module provides functionalities for ...
"""
from pydantic import Field

from common.models._custom_base_model import CustomBaseModel


class VccInfoModel(CustomBaseModel):
    card_number: str = Field(..., description='卡号', alias='cardNumber')
    card_type: str = Field(..., description="卡类型", alias='cardType')
    card_expire: str = Field(..., description='有效期', alias='cardExpire')
    card_holder: str = Field(..., description='持卡人姓名', alias='cardholder')
    security_code: str = Field(..., description='安全码', alias='securityCode')
    address: str = Field('', description='支付地址', alias='address')
    ext: dict = Field([], description='扩展字段', alias='ext')

    def last_name(self) -> str:
        return self.card_holder.split('/')[0]

    def first_name(self) -> str:
        return self.card_holder.split('/')[1]

    def full_name(self) -> str:
        return self.first_name() + " " + self.last_name()
