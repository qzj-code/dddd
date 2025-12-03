"""
Module: _bundle_info_model
Author: Ciwei
Date: 2024-10-07

Description: 
    This module provides functionalities for ...
"""
from typing import List, Optional

from pydantic import Field

from common.enums import CabinLevelEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.interior_service._baggage_info_model import BaggageInfoModel
from common.models.interior_service._catering_model import CateringInfoModel
from common.models.interior_service._low_fare_info_model import LowFareInfoModel
from common.models.interior_service._price_info_model import PriceInfoModel
from common.models.interior_service._seat_info_model import SeatInfoModel


class BundleInfoModel(CustomBaseModel):
    price_info: Optional[List[PriceInfoModel]] = Field(None, description="", alias='priceInfo')
    cabin_level: CabinLevelEnum = Field(..., description='舱位等级', alias='cabinLevel')
    cabin: str = Field(..., description='中转|分割，往返^分隔', alias='cabin')
    fare_basis: str = Field('', description='', alias='fareBasis')
    private_code: str = Field('', description='私有运价代码或网站优惠码', alias='privateCode')
    product_code: str = Field('', description='产品网站代码', alias='productCode')
    product_tag: str = Field('', description='产品类型，网站实际展示的产品类型', alias='productTag')
    price_tag: Optional[List] = Field([], description='价格标签，根据实际业务需求返回', alias='priceTag')
    available_count: int = Field(..., description='', alias='availableCount')
    key: Optional[str] = Field(None, description='', alias='key')
    id: Optional[str] = Field(None, description='关联id', alias='id')
    baggage_list: List[BaggageInfoModel] = Field([], description='', alias='baggageList')
    seat_list: List[SeatInfoModel] = Field([], description='', alias='seatList')
    catering_list: List[CateringInfoModel] = Field([], description='', alias='cateringList')
    ext: Optional[dict] = Field(None, description='', alias='ext')
    lowFareInfo: Optional[LowFareInfoModel] = Field(None, description='低价信息', alias='lowFareInfo')
    change_pnr: Optional[bool] = Field(False, description='低价信息', alias='changePnr')
