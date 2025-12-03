"""
Module: result_info_model
Author: likanghui
Date: 2024-10-15

Description:
    采购单票号信息模型
"""
from typing import Optional

from pydantic import Field

from common.enums import SegmentTypeEnum
from common.models._custom_base_model import CustomBaseModel


class TicketInfoModel(CustomBaseModel):
    airline_pnr: Optional[str] = Field(None, description="航司编码", alias="airlinePnr")
    pnr: Optional[str] = Field(None, description="PNR", alias="pnr")
    segment_index: int = Field(None, description="航段序号，用于多段拼接(0,1,2)", alias="segmentIndex")
    ticket_no: Optional[str] = Field(None, description="电子票号", alias="ticketNo")
    segment_type: Optional[SegmentTypeEnum] = Field(None, description="航段类型，0：去程，1：回程", alias="segmentType")
