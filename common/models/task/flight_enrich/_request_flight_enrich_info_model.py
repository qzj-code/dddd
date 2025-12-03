from typing import List

from pydantic import Field

from common.models import CustomBaseModel
from common.models.task._email_segment_list import EmailSegmentList


class RequestFlightEnrichInfoModel(CustomBaseModel):
    carrier: str = Field(..., description='航司')
    segment_list: List[EmailSegmentList] = Field([], description="航班行程信息列表", alias='segmentList')
    session_id: str = Field(..., description='请求标识', alias='sessionId')
    data_source: str = Field(..., description='数据源', alias='dataSource')
