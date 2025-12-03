from typing import Optional

from pydantic import Field

from common.models._custom_base_model import CustomBaseModel


class RegisterModel(CustomBaseModel):
    account: str = Field(..., description='账户名', alias='account')
    password: str = Field(..., description='账户密码', alias='password')
    mobile_country_code: str = Field(..., description="国际电话区号", alias='mobileCountryCode')
    mobile: str = Field(..., description='联系人电话', alias='mobile')
    email: str = Field(..., description='联系人邮箱', alias='email')
    email_password: Optional[str] = Field("", description='邮箱密码', alias='emailPassword')
