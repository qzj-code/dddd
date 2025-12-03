from typing import Optional

from pydantic import Field

from common.models._custom_base_model import CustomBaseModel


class ResponsePointsFlightModel(CustomBaseModel):
    sign: str = Field(..., description='接口鉴权标识', alias='sign')
    session_id: str = Field(..., description='请求标识', alias='sessionId')
    email: Optional[str] = Field('', description='联系人邮箱', alias='email')
    email_password: Optional[str] = Field('', description='邮箱密码', alias='emailPassword')
    account: Optional[str] = Field('', description='账户名', alias='account')
    password: Optional[str] = Field('', description='账户密码', alias='password')
    integral: Optional[int] = Field(None, description='积分余额', alias='Integral')
