"""
Module: _passenger_info_model
Author: Ciwei
Date: 2024-10-10

Description:
    乘客信息模型
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import Field, field_serializer

from common.enums import PassengerTypeEnum, GenderTypeEnum, CardTypeEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.task._ancillaries_baggage_info_model import AncillaryBaggageInfoModel
from common.models.task._seat_info_model import SeatInfoModel
from common.models.task._ticket_info_model import TicketInfoModel


class PassengerInfoModel(CustomBaseModel):
    passenger_type: PassengerTypeEnum = Field(..., description='乘客类型', alias="passengerType")
    name: str = Field(..., description='乘客名称', alias="name")
    gender: Optional[GenderTypeEnum] = Field(..., description='性别', alias="gender")
    birthday: Optional[datetime] = Field(..., description='生日', alias="birthday")
    card_type: Optional[CardTypeEnum] = Field(None, description='证件类型', alias="cardType")
    card_number: Optional[str] = Field(None, description='证件号', alias="cardNumber")
    card_expired: Optional[datetime] = Field(None, description='证件有效期', alias="cardExpired")
    issue_place: Optional[str] = Field(None, description='证件签发地', alias="issuePlace")
    mob_country_code: Optional[str] = Field(None, description='国际电话区号', alias="mobCountryCode")
    mobile: Optional[str] = Field(None, description='手机号', alias="mobile")
    nationality: Optional[str] = Field(None, description='国籍', alias="nationality")
    email: Optional[str] = Field(None, description='乘客邮箱', alias="email")
    baggage_list: Optional[List[AncillaryBaggageInfoModel]] = Field([], description='行李信息', alias="baggageList")
    ticket_info_list: Optional[List[TicketInfoModel]] = Field([], description="票号信息", alias="ticketInfoList")
    seat_info_list: Optional[List[SeatInfoModel]] = Field([], deprecated='座位信息', alias="seatInfoList")
    ticket_no: Optional[str] = Field('', deprecated='票号', alias="ticketNo")
    pnr: Optional[str] = Field('', deprecated='pnr', alias="pnr")
    address: Optional[str] = Field('', deprecated='地址', alias="address")

    @field_serializer('card_expired', 'birthday', when_used='json')
    def time_serializer(self, v):
        if v is None:
            return ''
        return v.strftime('%Y-%m-%d')

    def first_name(self):
        return self.name.split("/")[1]

    def last_name(self):
        return self.name.split("/")[0]

    def get_baggage_total_price(self):
        """
            获取行李总价
        Returns:

        """

        if not self.baggage_list:
            return Decimal(0)
        total_price = sum([x.amount for x in self.baggage_list])
        return total_price

    def get_total_price(self):
        return self.get_baggage_total_price()
