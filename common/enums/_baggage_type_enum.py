"""
Module: _baggage_type_enum
Author: Ciwei
Date: 2024-09-11

Description:
    行李类型
"""
from enum import Enum


class BaggageTypeEnum(Enum):
    HAULING_BAGGAGE = "1"  # 拖运行李
    HAND_LUGGAGE = "2"  # 手提行李
    HAND_BAG = "3"  # 手提包
