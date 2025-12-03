"""
Module: _card_type_enum
Author: Ciwei
Date: 2024-10-10

Description: 
    This module provides functionalities for ...
"""
from enum import Enum


class documentTypeEnum(Enum):
    PP = "PP"  # 护照
    JG = "JG"  # 军官证
    GA = "GA"  # 港澳通行证
    TW = "TW"  # 台湾通行证
    TB = "TB"  # 台胞证
    HX = "HX"  # 回乡证
    HY = "HY"  # 海员证
    QT = "QT"  # 其他
