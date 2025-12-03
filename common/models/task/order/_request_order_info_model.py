"""
Module: order_info_model
Author: Ciwei
Date: 2024-10-10

Description: 
    This module provides functionalities for ...
"""
from datetime import datetime
from typing import Optional, List

from pydantic import Field, model_validator

from common.enums import TripTypeEnum, PassengerTypeEnum, CabinLevelEnum, PayTypeEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.task._contact_info_model import ContactInfo
from common.models.task._fare_info_model import FareInfoModel
from common.models.task._passenger_info_model import PassengerInfoModel
from common.models.task._vcc_info_model import VccInfoModel


class RequestOrderInfoModel(CustomBaseModel):
    session_id: str = Field(..., description='请求标识', alias='sessionId')
    office: str = Field(..., description='主Office', alias='office')
    connect_office: str = Field(..., description='子office', alias='connectOffice')
    trip_type: TripTypeEnum = Field(..., description="行程类型", alias='tripType')
    origin: str = Field(..., description='出发地', alias='origin')
    destination: str = Field(..., description='目的地', alias='destination')
    dep_date: datetime = Field(..., description='出发日期', alias='depDate')
    ret_date: Optional[datetime] = Field(None, description='返程日期', alias='retDate')
    cabin_level: CabinLevelEnum = Field(..., description="舱位等级", alias='cabinLevel')
    private_code: Optional[List[str]] = Field([], description='私有运价代码', alias="privateCode")
    pnr: Optional[str] = Field(None, description='pnr', alias='pnr')
    pnr_info: Optional[str] = Field(None, description='pnr编码详情', alias='pnrInfo')
    ticket_carrier: str = Field(..., description='开票航司', alias='ticketCarrier')
    currency: str = Field(..., description='币种', alias='currency')
    price_threshold: Optional[str] = Field('0', description='变价阈值', alias='priceThreshold')
    flight_change_time_threshold: Optional[str] = Field("", description='航变时间阈值，格式：0-120',
                                              alias='flightChangeTimeThreshold')
    fare: FareInfoModel = Field(..., description='航班价格列表信息', alias='fare')
    passenger_list: List[PassengerInfoModel] = Field(..., description='乘客列表', alias='passengerList')
    contact_info: ContactInfo = Field(..., description='联系人信息', alias='contactInfo')
    vcc_info: Optional[VccInfoModel] = Field(None, description='vcc信息', alias='vccInfo')
    ext: dict = Field(..., description='扩展', alias='ext')
    need_pay: Optional[bool] = Field(None, description='是否支付', alias='needPay')
    pay_type: Optional[PayTypeEnum] = Field(None, description='支付方式', alias='payType')

    @model_validator(mode='before')
    def required_check(cls, value):
        required_fields = ['sessionId', 'office', 'tripType', 'origin', 'destination', 'depDate', 'cabinLevel',
                           'ticketCarrier', 'currency', 'fare', 'passengerList', 'contactInfo', ]
        for field in required_fields:
            if field not in value:
                raise ValueError(f'{field} is required')
        return value
