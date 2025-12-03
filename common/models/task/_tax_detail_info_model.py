"""
Module: _tax_detail_info_model
Author: Ciwei
Date: 2024-10-06

Description: 
    This module provides functionalities for ...
"""
from decimal import Decimal

from pydantic import Field

from common.models._custom_base_model import CustomBaseModel


class TaxDetailInfoModel(CustomBaseModel):
    tax_amount: Decimal = Field(..., description='税项金额', alias='taxAmount')
    tax_name: Decimal = Field(..., description='税项名称', alias='taxName')
