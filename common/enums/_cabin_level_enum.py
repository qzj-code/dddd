"""
Module: _cabin_level_enum
Author: Ciwei
Date: 2024-09-09

Description:
    舱级
"""
from enum import Enum


class CabinLevelEnum(Enum):
    ECONOMY = "Y"  # 经济舱
    SUPER_ECONOMY = "S"  # 超级经济舱
    BUSINESS = "C"  # 公务舱
    FIRST = "F"  # 头等舱
