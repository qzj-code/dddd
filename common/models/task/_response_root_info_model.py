"""
Module: _response_root_info_model
Author: Ciwei
Date: 2024-10-11

Description: 
    This module provides functionalities for ...
"""
from typing import Any

from pydantic import Field

from common.models._custom_base_model import CustomBaseModel


class ResponseRootInfoModel(CustomBaseModel):
    code: int = Field(..., description='程序状态，0:查询成功;1:查询失败', alias='code')
    msg: str = Field(..., description='message', alias='msg')
    success: bool = Field(..., description='success', alias='success')
    data: Any = Field(..., description='data', alias='data')
