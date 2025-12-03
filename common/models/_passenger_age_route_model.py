"""
@Project     : PassengerAgeRouteModel
@Author      : ciwei
@Date        : 2024/10/15 17:00
@Description :
@versions    : 1.0.0.0
"""

from pydantic import BaseModel, Field

from ..enums import PassengerTypeEnum


class PassengerAgeRouteModel(BaseModel):
    routeName: PassengerTypeEnum = Field(description="规则名称")
    minAge: int = Field(description="最小年龄")
    maxAge: int = Field(description="最大年龄")