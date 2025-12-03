"""
Module: _fare_info_model
Author: Ciwei
Date: 2024-10-06

Description: 
    This module provides functionalities for ...
"""
from datetime import datetime
from typing import Optional, List

from pydantic import Field, field_serializer

from common.models._custom_base_model import CustomBaseModel
from common.models.task._low_fare_info_model import LowFareInfoModel
from common.models.task._price_info_model import PriceInfoModel
from common.models.task._segment_info_model import SegmentInfoModel
from common.models.task._tax_detail_info_model import TaxDetailInfoModel


class FareInfoModel(CustomBaseModel):
    fare_key: Optional[str] = Field(None, description="费用key", alias='fareKey')
    currency: str = Field(..., description="币种", alias='currency')
    data_source: str = Field(..., description="数据源", alias='dataSource')
    last_purchase_time: Optional[datetime] = Field(None, description="最后采购时间", alias='lastPurchaseTime')
    office: str = Field('', description='主office', alias='office')
    connect_office: str = Field('', description='子office', alias='connectOffice')
    price_type: str = Field(..., description='价格类型', alias='priceType')
    private_code: str = Field('', description='私有运价代码或网站优惠码', alias='privateCode')
    product_tag: str = Field('', description='产品类型，网站实际展示的产品类型', alias='productTag')
    ticket_carrier: str = Field(..., description='开票航司，若无返回实际航司', alias='ticketCarrier')
    price_tag: Optional[List] = Field([], description='价格标签，根据实际业务需求返回', alias='priceTag')
    change_pnr: bool = Field(True, description='价格标签，根据实际业务需求返回', alias='changePnr')
    refund_info: Optional[str] = Field(None, description='退票规则信息', alias='refundInfo')
    change_info: str = Field('', description='改签规则信息', alias='changeInfo')
    price_list: List[PriceInfoModel] = Field(..., description='价格列表', alias='priceList')
    segment_list: List[SegmentInfoModel] = Field(..., description='航段列表', alias='segmentList')
    tax_detail: Optional[List[TaxDetailInfoModel]] = Field([], description='税项列表', alias='taxDetail')
    lowFareInfo: Optional[LowFareInfoModel] = Field(None, description='低价信息', alias='lowFareInfo')
    ext: Optional[dict] = Field({}, description='扩展', alias='ext')

    @field_serializer('last_purchase_time', when_used='json')
    def time_serializer(self, v):
        try:
            return v.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            return None