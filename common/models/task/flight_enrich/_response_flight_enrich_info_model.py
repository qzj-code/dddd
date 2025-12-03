from typing import List

from pydantic import Field

from common.models import CustomBaseModel
from common.models.task._email_segment_list import EmailSegmentList


class ResponseFlightEnrichInfoModel(CustomBaseModel):
    is_update: bool = Field(False, description='是否更新', alias='isUpdate')
    segment_list: List[EmailSegmentList] = Field([], description="航班行程信息列表", alias='segmentList')
