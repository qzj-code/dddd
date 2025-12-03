"""
Module: _request_order_detail_info_model
Author: Ciwei
Date: 2024-10-17

Description: 
    This module provides functionalities for ...
"""
from typing import List, Optional

from pydantic import Field, model_validator

from common.models._custom_base_model import CustomBaseModel
from common.models.task._contact_info_model import ContactInfo


class RequestOrderDetailInfoModel(CustomBaseModel):
    connect_office: str = Field(..., description='子office', alias='connectOffice')
    data_source: str = Field(..., description='数据源', alias='dataSource')
    office: str = Field(..., description='主office', alias='office')
    order_no: str = Field(..., description='订单号', alias='orderNo')
    pnr: str = Field(..., description='pnr', alias='pnr')
    session_id: str = Field(..., description='请求标识', alias='sessionId')
    passenger_name_list: Optional[List] = Field([], description='乘机人姓名列表', alias='passengerNameList')
    contact_info: ContactInfo = Field(..., description='联系人信息', alias='contactInfo')
    ext: dict = Field(..., description='扩展信息', alias='ext')

    @model_validator(mode='before')
    def required_check(cls, value):
        required_fields = ['connectOffice', 'dataSource', 'office', 'orderNo', 'pnr', 'sessionId',
                           'contactInfo']
        for field in required_fields:
            if field not in value:
                raise ValueError(f'{field} is required')
        return value
