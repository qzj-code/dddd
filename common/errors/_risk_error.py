from common.errors._base_state_enum import BaseStateEnum
from common.errors._my_base_error import MyBaseError


class RiskStateEnum(BaseStateEnum):
    AKM_TLS_CHECK_FAILURE = "AkmTls验证未通过"
    AKM_CHECK_FAILURE = "Akm验证未通过"
    GOOGLE_CHECK_FAILURE = "Google验证未通过"
    CLOUD_FLARE_CHECK_FAILURE = "CloudFlare验证未通过"
    INCAPSULA_CHECK_FAILURE = "Incapsula验证未通过"
    HCAPTCHA_CHECK_FAILURE = "Hcaptcha验证未通过"
    RECAPTCHA_CHECK_FAILURE = "Recaptcha验证未通过"
    KASADA_CHECK_FAILURE = "Kasada验证未通过"
    ALI_SLIDING_CHECK_FAILURE = "Ali滑块验证未通过"
    PX_CHECK_FAILUR = "PX验证未通过"

    GEETEST_CHECK_FAILURE = "Geetest验证未通过"



class RiskError(MyBaseError):
    def __init__(self, risk_enum, *args):
        message = risk_enum.value.format(args)
        super().__init__(state_enum=risk_enum, message=message)
