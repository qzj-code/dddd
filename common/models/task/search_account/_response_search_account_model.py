"""
Module: _response_search_flight_model
Author: Ciwei
Date: 2024-10-11

Description: 
    This module provides functionalities for ...
"""
from typing import Optional

from pydantic import Field

from common.models.task.register import ResponsePointsFlightModel


class ResponseSearchAccountModel(ResponsePointsFlightModel):
    mob_country_code: Optional[str] = Field("", description='国家区号', alias='mobCountryCode')
    mobile: Optional[str] = Field("", description='注册手机号', alias='mobile')
    registrant: Optional[str] = Field("", description='注册人', alias='registrant')
    account_number: Optional[str] = Field("", description='会员账号', alias='accountNumber')
