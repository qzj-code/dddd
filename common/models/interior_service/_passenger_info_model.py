"""
Module: _passenger_info_model
Author: likanghui
Date: 2024-10-06

Description:
    内部Passenger模型
"""
import decimal
from datetime import datetime
from typing import Optional, List, Union

from pydantic import Field, BaseModel, field_serializer

from common.enums import PassengerTypeEnum, GenderTypeEnum, CardTypeEnum, AncillariesTypeEnum
from common.models.interior_service._ancillaries_info_model import AncillariesInfoModel
from common.models.interior_service._baggage_info_model import BaggageInfoModel
from common.models.interior_service._catering_model import CateringInfoModel
from common.models.interior_service._seat_info_model import SeatInfoModel
from common.models.task import TicketInfoModel


class PassengerInfoModel(BaseModel):
    id: Optional[str] = Field(None, alias='id')
    passenger_type: PassengerTypeEnum = Field(..., description='乘客类型', alias="passengerType")
    name: str = Field(..., description='乘客名称', alias="name")
    gender: Optional[GenderTypeEnum] = Field(None, description='性别', alias="gender")
    birthday: datetime = Field(None, description='生日', alias="birthday")
    card_type: Optional[CardTypeEnum] = Field(None, description='证件类型', alias="cardType")
    card_number: Optional[str] = Field(None, description='证件号', alias="cardNumber")
    card_expired: Optional[datetime] = Field(None, description='证件有效期', alias="cardExpired")
    issue_place: Optional[str] = Field(None, description='证件签发地', alias="issuePlace")
    mob_country_code: Optional[str] = Field(None, description='国际电话区号', alias="mobCountryCode")
    mobile: Optional[str] = Field(None, description='手机号', alias="mobile")
    nationality: Optional[str] = Field(None, description='国籍', alias="nationality")
    email: Optional[str] = Field(None, description='乘客邮箱', alias="email")
    ticket_info_list: Optional[List[TicketInfoModel]] = Field([], description="票号信息", alias="ticketInfoList")
    ancillaries_list: List[AncillariesInfoModel] = Field([], description='辅营信息列表', alias="AncillariesInfo")
    purchasing_ancillaries_list: List[AncillariesInfoModel] = Field([], description='需要采购的辅营信息',
                                                                    alias="AncillariesInfo")

    @field_serializer('card_expired', 'birthday', when_used='json')
    def time_serializer(self, v):
        if v is None:
            return ''
        return v.strftime('%Y-%m-%d')

    def first_name(self):
        """
            获取乘客名
        Returns:

        """
        return self.name.split("/")[1]

    def last_name(self):
        """
            获取乘客姓
        Returns:

        """
        return self.name.split("/")[0]

    def get_purchasing_ancillaries(self, ancillaries_type: AncillariesTypeEnum) -> Union[
        List[BaggageInfoModel], List[SeatInfoModel], List[CateringInfoModel], List]:
        return next((x.data for x in self.purchasing_ancillaries_list if x.code == ancillaries_type), [])

    def get_ancillaries(self, ancillaries_type: AncillariesTypeEnum) -> Union[
        List[BaggageInfoModel], List[SeatInfoModel], List[CateringInfoModel], List]:
        return next((x.data for x in self.ancillaries_list if x.code == ancillaries_type), [])

    def get_purchasing_baggage(self) -> List[BaggageInfoModel]:
        # 遍历辅营列表
        for purchasing_info in self.purchasing_ancillaries_list:
            # 判断辅营类型是否为行李
            if purchasing_info.code != AncillariesTypeEnum.LUGGAGE:
                continue

            return purchasing_info.data
        return []

    def get_purchasing_baggage_weight(self, flight_number: Optional[str] = None):
        """
            获取采购所需行李重量
        Returns:

        """
        total_weight = 0

        for baggage_info in self.get_purchasing_baggage():

            # 过滤指定航班行李
            if flight_number and baggage_info.flight_number != flight_number:
                continue
            total_weight += baggage_info.total_weight

        return total_weight

    def get_baggage_total_price(self):
        """
            获取行李总价格
        Returns:

        """
        amount = decimal.Decimal(0)
        for ancillaries_info in self.ancillaries_list:
            if ancillaries_info.code != AncillariesTypeEnum.LUGGAGE:
                continue

            for baggage_info in ancillaries_info.data:
                amount += baggage_info.amount
        return amount

    def get_total_price(self):
        baggage_total_price = self.get_baggage_total_price()
        return baggage_total_price

    def add_ancillaries_data(self,
                             data: Union[BaggageInfoModel,
                             SeatInfoModel, CateringInfoModel],
                             ancillaries_type: AncillariesTypeEnum,
                             purchasing: bool):
        ancillaries_info = next(
            (x for x in (self.purchasing_ancillaries_list if purchasing else self.ancillaries_list) if
             x.code == ancillaries_type), None)

        if ancillaries_info is None:
            ancillaries_info = AncillariesInfoModel.model_validate({
                'code': ancillaries_type
            })
            if purchasing:
                self.purchasing_ancillaries_list.append(ancillaries_info)
            else:
                self.ancillaries_list.append(ancillaries_info)

        if isinstance(data, BaggageInfoModel):
            data.passenger_type = self.passenger_type
        ancillaries_info.data.append(data)

    def get_baggage_infos(self) -> List[BaggageInfoModel]:
        """
            获取全部行李信息
        Returns:

        """

        return next((x.data for x in self.ancillaries_list if x.code == AncillariesTypeEnum.LUGGAGE), [])
