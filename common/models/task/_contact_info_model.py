"""
Module: _contact_info_model
Author: Ciwei
Date: 2024-10-10

Description: 
    This module provides functionalities for ...
"""
from pydantic import Field

from common.models._custom_base_model import CustomBaseModel


class ContactInfo(CustomBaseModel):
    name: str = Field(..., description='联系人姓名', alias='name')
    mobile_country_code: str = Field(..., description="国际电话区号", alias='mobileCountryCode')
    mobile: str = Field(..., description='联系人电话', alias='mobile')
    email: str = Field(..., description='联系人邮箱', alias='email')

    def first_name(self):
        return self.name.split("/")[1]

    def last_name(self):
        return self.name.split("/")[0]
