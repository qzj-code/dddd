"""
Module: _root_model
Author: Ciwei
Date: 2024-09-13

Description: 
    This module provides functionalities for ...
"""
from typing import Union, Optional

from pydantic import Field

from common.enums import TaskTypeEnum
from common.models._custom_base_model import CustomBaseModel
from common.models.task.order import RequestOrderInfoModel
from common.models.task.search import RequestSearchFlightModel
from common.models.task.verify import RequestVerifyPriceModel


class RequestRootInfoModel(CustomBaseModel):
    task_id: str = Field(..., description="任务ID", alias="taskId")
    task_type: TaskTypeEnum = Field(..., description="任务类型", alias="taskType")
    task_expire_time: Optional[int] = Field(None, description='任务过期时间',alias="taskExpireTime")
    task_data: Union[RequestSearchFlightModel, RequestVerifyPriceModel, RequestOrderInfoModel] = Field(...,
                                                                                                       description="任务数据",
                                                                                                       alias="taskData")
