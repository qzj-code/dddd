"""
Module: _proxy_info_model
Author: Ciwei
Date: 2024-09-13

Description:
    代理信息模型
"""
from typing import Optional

from pydantic import BaseModel, Field


class ProxyInfoModel(BaseModel):
    host: str = Field(..., description='代理地址')
    port: int = Field(..., description='代理端口')
    username: str = Field(..., description='用户名')
    password: str = Field(..., description='密码')
    user_format_text: str = Field(..., description='代理用户名格式文本', alias="userFormatText")
    region: str = Field(..., description="区域")
    sess_time: int = Field(..., description="有效期", alias="sessTime")
    session: Optional[str] = Field(None, description="会话标识")

    def get_proxy_info_string(self):
        user_string = self.user_format_text.format(username=self.username,
                                                   region=self.region,
                                                   sess_time=self.sess_time,
                                                   session=self.session)
        return f'{user_string}:{self.password}@{self.host}:{self.port}'

    def get_proxy_username(self):
        user_string = self.user_format_text.format(username=self.username,
                                                   region=self.region,
                                                   sess_time=self.sess_time,
                                                   session=self.session)
        return user_string
