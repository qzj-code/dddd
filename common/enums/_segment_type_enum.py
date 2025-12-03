"""
Module: _segment_type_enum
Author: Ciwei
Date: 2024-09-11

Description: 
    航段类型
"""
from enum import Enum


class SegmentTypeEnum(Enum):
    TRIP = 1
    RETURN_TRIP = 2
