"""
@Project     : CommonStateEnum
@Author      : likanghui
@Date        : 2024/10/12 11:20
@Description : 
@versions    : 1.0.0.0
"""

from ._base_state_enum import BaseStateEnum
from ._my_base_error import MyBaseError


class CommonStateEnum(BaseStateEnum):
    """
    自定义状态码
    """
    SUCCESS = "成功"
    FAILURE = "失败"
    INTERNAL_SYSTEM_ERROR = "服务器异常"
    SERVICE_ERROR = "业务处理异常"
    CUSTOM_SERVICE_ERROR = "业务内部错误[{}]"
    TASK_REQUEST_TIMEOUT = "任务超时"
    BOOKING_PAY_FAIL = "付款失败[{}]"
    PAYMENT_GET_NECESSARY_DATA_FAILURE = "付款未能取得所需的资料[{}]"
    PAYMENT_PROCESS_NOT_MEET_EXPECTATIONS = "支付流程未达到预期结果[{}]"
    PAYMENT_STATUS_NOT_EXPECTATIONS = "支付状态未达到预期结果[{}]"
    CHECK_FLIGHT_DATA_FAILURE = "验证航班[{}]信息不符，实际[{}]，业务传入[{}]"
    CHECK_FLIGHT_FARE_FAILURE = "验证航班[票价]信息不符，实际[{}]，业务传入[{}]，差额[{}]"
    PAY_ITINERARY_FAILURE = "支付后行程单获取失败[{}]"
    TICKET_NUMBER_STATUS_PAYMENT = "提交付款后票号状态没达到预期，实际[{}]"

    BOOKING_STATE_CHECK_FAILURE = "状态未通过验证，VCC状态[{}]"
    BOOKING_NO_PNR = "未找到PNR[{}]"
    BOOKING_NO_PAYMENT_RECORD_FOUND = "未找到付款记录"
    BOOKING_UNKNOWN_STATE = "未知状态[{}]"
    BOOKING_SEARCH_FLIGHT_FAILURE = "预订选择航班失败"

    SERVICE_RESPONSE_EXCEPTION = "目标服务器响应异常[{}],Method[{}]"
    SERVICE_RESPONSE_CODE_NOT_EXPECTATIONS = "服务器响应状态未达到预期[{}],Method[{}]"

    USER_APPLY_EMAIL_ACCOUNT_FAILED = "申请邮箱账号失败"
    SERVICE_RESPONSE_DATA_NOT_ANTICIPATE = "服务器响应数据未达到预期[{}]"
    CURRENCY_CONVERSION_FAILURE_NOT_CURRENCY_DATA = "转换币种失败，无币种数据"


class CommonError(MyBaseError):
    """
    自定义异常类
    """
    def __init__(self, CommonStateEnum, *args):
        message = CommonStateEnum.value.format(args)
        super().__init__(state_enum=CommonStateEnum, message=message)
