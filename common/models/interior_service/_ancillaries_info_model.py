"""
Module: _business_info_model
Author: likanghui
Date: 2024-10-17

Description:
    辅营模型
"""
from typing import List, Union

from pydantic import Field

from common.enums import AncillariesTypeEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.interior_service._baggage_info_model import BaggageInfoModel
from common.models.interior_service._catering_model import CateringInfoModel
from common.models.interior_service._seat_info_model import SeatInfoModel


class AncillariesInfoModel(CustomBaseModel):
    code: AncillariesTypeEnum = Field('', description='辅营代码', alias='code')
    data: Union[List[BaggageInfoModel], List[SeatInfoModel], List[CateringInfoModel]] = Field([],
                                                                                              description='辅营数据',
                                                                                              alias='data')
