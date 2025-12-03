"""
Module: _vcc_type_enum
Author: Ciwei
Date: 2024-12-09

Description: 
    This module provides functionalities for ...
"""
from enum import Enum


class VccTypeEnum(Enum):
    CA = "MC"
    VI = "VI"


    @classmethod
    def get_member_names(cls):
        return list(VccTypeEnum.__members__.keys())