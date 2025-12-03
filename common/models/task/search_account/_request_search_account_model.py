"""
Module: _search_flight_model
Author: Ciwei
Date: 2024-09-09

Description:
    查询任务模型
"""

from typing import Optional

from pydantic import Field, model_validator

from common.models._custom_base_model import CustomBaseModel
from common.models.task._ext_info_model import ExtInfoModel


class RequestSearchAccountModel(CustomBaseModel):
    session_id: str = Field(..., description='sessionId', alias='sessionId')
    office: str = Field(..., description='主Office', alias='office')
    data_source: str = Field(..., description='数据来源', alias='dataSource')
    connect_office: str = Field(..., description='子office', alias='connectOffice')
    email: Optional[str] = Field("", description="邮箱", alias='email')
    email_password: Optional[str] = Field("", description="邮箱密码", alias='emailPassword')
    account: Optional[str] = Field("", description="账户账号", alias='account')
    password: Optional[str] = Field("", description="账户密码", alias='password')
    ext: Optional[ExtInfoModel] = Field(ExtInfoModel(), description="拓展字段", alias="ext")

    @model_validator(mode='before')
    def required_check(cls, value):
        required_fields = ['sessionId', 'office', 'connectOffice', 'dataSource', 'email', 'emailPassword', 'account',
                           'password', ]
        for field in required_fields:
            if field not in value:
                raise ValueError(f'{field} is required')
        return value
