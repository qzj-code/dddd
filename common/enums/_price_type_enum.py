"""
Module: _price_type_enum
Author: Ciwei
Date: 2024-10-07

Description: 
    This module provides functionalities for ...
"""
from enum import Enum


class PriceTypeEnum(Enum):
    ORDINARY = "ORDINARY"  # 普通
    MEMBER = "MEMBER"  # 会员
    CHANGE_KEY = "CHANGE_KEY"  # 换KEY
