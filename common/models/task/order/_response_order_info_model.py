"""
Module: order_info_model
Author: likanghui
Date: 2024-10-15

Description:
    This module provides functionalities for ...
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from pydantic import Field, field_serializer, field_validator

from common.models._custom_base_model import CustomBaseModel
from common.models.task._ext_info_model import ExtInfoModel
from common.models.task._passenger_info_model import PassengerInfoModel
from common.models.task._pay_info_model import PayInfoModel
from common.models.task._price_info_model import PriceInfoModel
from common.models.task._segment_info_model import SegmentInfoModel


class ResponseOrderInfoModel(CustomBaseModel):
    session_id: str = Field(..., description='请求标识', alias='sessionId')
    sign: str = Field(..., description='接口鉴权标识', alias='sign')
    order_no: str = Field('', description='订单号', alias='orderNo')
    product_tag: str = Field(..., description='套餐名', alias='productTag')
    order_state: str = Field(..., description='订单状态', alias='orderState')
    currency: str = Field(..., description='货币', alias='currency')
    issued: bool = Field(..., description='是否已出票', alias='issued')
    create_time: Optional[datetime] = Field(None, description='生单时间', alias='createTime')
    last_ticket_time: Optional[datetime] = Field(None, description='支付时间', alias='lastTicketTime')
    ticket_time: Optional[datetime] = Field(None, description='出票时间', alias='ticketTime')
    pnr: str = Field(..., description='pnr', alias='pnr')
    airline_pnr: str = Field(..., description='航司编码', alias='airlinePnr')
    ticket_carrier: str = Field('', description='实际开票航司', alias='ticketCarrier')
    office_info: Optional[dict] = Field(None, description=' office信息', alias='officeInfo')
    passenger_list: List[PassengerInfoModel] = Field(..., description='乘客信息', alias='passengerList')
    price_list: List[PriceInfoModel] = Field([], description='价格信息', alias='priceList')
    segment_list: List[SegmentInfoModel] = Field([], description='航段信息', alias='segmentList')
    pay_info: Optional[PayInfoModel] = Field(None, description='支付信息', alias='payInfo')
    ext: Optional[ExtInfoModel] = Field(None, description='扩展信息', alias='ext')
    total_price:Optional[Decimal] = Field(None,description='总支付金额',alias="totalPrice")

    @field_serializer('create_time', 'ticket_time', 'last_ticket_time', when_used='json')
    def time_serializer(self, v):
        if v is None:
            return None
        return v.strftime('%Y-%m-%d %H:%M:%S')

    @field_validator('total_price', mode='before')
    def decimal_validator(cls, v: Decimal) -> Optional[Decimal]:
        try:
            if not isinstance(v, Decimal):
                v = Decimal(str(v))
            v = v.quantize(Decimal('0.00'))
            return v
        except InvalidOperation as e:
            return None

    @field_serializer('total_price', when_used='json')
    def decimal_serializer(self, v):
        try:
            return self.convert_data_serializer_json(v)
        except InvalidOperation:
            return None