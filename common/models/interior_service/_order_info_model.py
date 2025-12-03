"""
Module: _order_info_model
Author: likanghui
Date: 2024-10-17

Description:
    内部订单信息模型
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import Field, field_validator, field_serializer

from common.enums import OrderStateEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.interior_service import SegmentInfoModel, PassengerInfoModel, BundleInfoModel
from common.models.task import PayInfoModel, ExtInfoModel


class OrderInfoModel(CustomBaseModel):
    order_no: Optional[str] = Field('', description='订单号', alias="orderNo")
    order_state: Optional[OrderStateEnum] = Field(None, description='订单状态', alias="orderState")
    currency: Optional[str] = Field('', description='支付货币', alias="currency")
    issued: Optional[bool] = Field(False, description='是否开票，true:是；false:否', alias="issued")
    create_time: Optional[datetime] = Field(None, description='生单时间', alias="createTime")
    last_ticket_time: Optional[datetime] = Field(None, description='最晚支付时间', alias="lastTicketTime")
    ticket_time: Optional[datetime] = Field(None, description='实际出票时间', alias="ticketTime")
    pnr: Optional[str] = Field('', description='pnr', alias="pnr")
    airline_pnr: Optional[str] = Field('', description='航司pnr', alias="airlinePnr")
    ticket_carrier: Optional[str] = Field('', description='实际开票航司', alias='ticketCarrier')
    office_info: Optional[dict] = Field(None, description=' office信息', alias='officeInfo')
    passengers: List[PassengerInfoModel] = Field([], description='乘机人列表', alias="passengers")
    segments: Optional[List[SegmentInfoModel]] = Field([], description='航班信息列表', alias="segments")
    payment_info: Optional[PayInfoModel] = Field(None, description='支付信息', alias="paymentInfo")
    ext: Optional[ExtInfoModel] = Field(None, description='扩展信息', alias='ext')
    bundle_info: Optional[BundleInfoModel] = Field([], deprecated='航班费用信息', alias="bundleInfo")
    total_price: Optional[Decimal] = Field(Decimal(0), description='总支付金额', alias="totalPrice")

    @field_validator('total_price', mode='before')
    def decimal_validator(cls, v: Decimal) -> Optional[Decimal]:
        if not v:
            return None
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        v = v.quantize(Decimal('0.00'))
        return v

    @field_serializer('total_price', when_used='json')
    def decimal_serializer(self, v):
        return self.convert_data_serializer_json(v)