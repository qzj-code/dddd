from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, constr, field_validator

from common.models import CustomBaseModel


class SegStatusEnum(Enum):
    UN = "UN"  # 取消
    TK = "TK"  # 新航班


class EmailSegmentList(CustomBaseModel):
    arr_airport: Optional[constr(min_length=3, max_length=3)] = Field(None, alias='arrAirport')
    dep_airport: Optional[constr(min_length=3, max_length=3)] = Field(None, alias='depAirport')
    arr_time: str = Field("", description="到达时间", alias='arrTime')
    dep_time: str = Field("", description="起飞时间", alias='depTime')
    dep_date: str = Field("", description="航班日期", alias='depDate')
    flight_number: str = Field("", description="航班号", alias='flightNumber')
    seg_status: SegStatusEnum = Field(..., description="航班状态", alias='segStatus')
    seg_num: int = Field(1, description="航段数", alias='segNum')
    arr_term: str = Field("", description="到达航站楼", alias='arrTerm')
    dep_term: str = Field("", description="起飞航站楼", alias='depTerm')
    cabin: str = Field("", description="舱位", alias='cabin')

    @field_validator("arr_time", "dep_time")
    def validate_time_format(cls, value):
        # 判断是否为8位或12位的纯数字
        if value == "":
            return value
        if not (len(value) in (8, 12) and value.isdigit()):
            raise ValueError("时间必须是 8 位或 12 位的纯数字")
        return value

    @field_validator('dep_date')
    def validate_dep_data(cls, value):
        if value == "":
            return value
        try:
            # 尝试将字符串解析为 'YYYY-MM-DD' 格式
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("dep_data 必须是 'YYYY-MM-DD' 格式的有效日期")
        return value

    @field_validator('flight_number')
    def remove_whitespace(cls, value):
        return value.replace(" ", "")

    class Config:
        use_enum_values = True  # 自动将枚举对象转换为其值

    @field_validator("arr_airport", "dep_airport", mode="before")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v
