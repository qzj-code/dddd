from pydantic import Field, model_validator

from common.models._custom_base_model import CustomBaseModel
from common.models.task import ExtInfoModel


class RequestCancelInfoModel(CustomBaseModel):
    session_id: str = Field(..., description='请求标识', alias='sessionId')
    office: str = Field(..., description='主Office', alias='office')
    pnr: str = Field(..., description='pnr', alias='pnr')
    ext: ExtInfoModel = Field('', description='扩展', alias='ext')

    @model_validator(mode='before')
    def required_check(cls, value):
        required_fields = ['sessionId', 'office', 'pnr', 'pnr', 'ext']
        for field in required_fields:
            if field not in value:
                raise ValueError(f'{field} is required')
        return value
