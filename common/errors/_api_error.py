from common.errors._base_state_enum import BaseStateEnum
from common.errors._my_base_error import MyBaseError


class ApiStateEnum(BaseStateEnum):
    ERROR_INFO = "第三方API错误：{}"
    CLOUD_FLARE_SOLUTION_FAILURE = "CloudFlare求解失败"
    HCAPTCHA_SOLUTION_FAILURE = "Hcaptcha求解失败"
    ALI_SLIDING_SOLUTION_FAILURE = "阿里滑块求解失败"
    AKM_SOLUTION_FAILURE = "AKM求解失败"
    RECAPTCHA_SOLUTION_FAILURE = "Recaptcha求解失败"
    GEETEST_SOLUTION_FAILURE = "Geetest求解失败"
    SBSD_SOLUTION_FAILURE = "SBSD求解失败"
    DX_SOLUTION_FAILURE = "顶象验证码求解失败"
    INCAPSULA_SOLUTION_FAILURE = "incapsula求解失败"


class APIError(MyBaseError):
    def __init__(self, api_enum, *args):
        message = api_enum.value.format(args)
        super().__init__(state_enum=api_enum, message=message)
