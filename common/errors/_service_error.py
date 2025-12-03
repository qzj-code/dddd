"""
Module: _service_state_enum
Author: Ciwei
Date: 2024-10-05

Description: 
    This module provides functionalities for ...
"""
from common.errors._base_state_enum import BaseStateEnum
from common.errors._my_base_error import MyBaseError
from common.utils import LogUtil


class ServiceStateEnum(BaseStateEnum):
    SERVICE_ERROR = "业务错误[{}]"
    NECESSARY_DATA_MISSING = "必要数据缺失[{}]"
    INVALID_DATA = "非法数据[{}]"
    INTERNAL_ERROR = "内部错误"
    RATE_CONTROL = "速率控制"

    SEARCH_FLIGHT_DATA_SUCCESS = "查询航班数据成功"
    VERIFY_FLIGHT_DATA_SUCCESS = "验证航班数据成功"
    SEARCH_ORDER_DETAIL_SUCCESS = "查询订单详情成功"
    ORDER_FLIGHT_DATA_SUCCESS = "生单成功"
    ORDER_FLIGHT_DATA_FAILURE = "生单失败"
    SEARCH_EXCHANGERATE_SUCCESS = "查询汇率数据成功"
    REGISTER_SUCCESS = "账户注册成功"
    SEARCH_ACCOUNT_SUCCESS = "查询账户信息成功"
    GATEWAY_TIMEOUT = "渠道网关超时"
    NO_FLIGHT_DATA = "无航班数据"
    INVALID_IP_ADDRESS = "异常IP地址"
    EXCHANGE_SUCCESS = "积分兑换成功"

    TICKET_NUMBER_INFO_MISTAKE = "票号信息错误"
    BOOKING_PAYMENT_DECLINED = "支付拒绝"
    BOOKING_PAYMENT_SUCCESS = "支付成功"
    BOOKING_CANCEL_DECLINED = "取消失败"
    BOOKING_CANCEL_SUCCESS = "取消成功"
    BOOKING_REFUND_SUCCESS = "退票成功"
    BOOKING_REFUND_FAILURE = "退票失败"
    SEARCH_BAGGAGE_DATA_SUCCESS = "查询行李数据成功"
    NO_BAGGAGE_DATA = "无行李数据"
    CREATE_CARD_SUCCESS = "开卡成功"
    CREATE_CARD_FAILURE = "开卡失败:{}"

    BOOKING_FAILURE_PAYMENT_STATE_CHECK_NOT_PASS = "支付状态检查未通过[{}]"
    BOOKING_FLIGHT_INFO_WEB_AND_OTA_DISCREPANCY = "航班信息[{}]与生单请求不符，生单请求[{}]，实际[{}]"
    BOOKING_FLIGHT_FARE_INFO_WEB_AND_OTA_DISCREPANCY = "航班信息[费用]与生单请求不符，生单请求[{}]，实际[{}]，差额[{}]"
    BOOKING_FAILURE_PRICE_CHECK_NOT_PASS = "乘客价格检查未通过，生单请求总价格[{}{}]，实际总价格[{}{}]，差额[{}{}]"
    BOOKING_FAILURE_CURRENCY_MISMATCH_ERROR = "货币类型不匹配，生单请求货币[{}]，实际货币[{}]"
    BOOKING_FAILURE_BAGGAGE_WEIGHT_CHECK_NOT_PASS = "乘客行李重量检查未通过，乘客[{}]，生单请求要求[{}]，实际限重[{}]"
    BOOKING_FAILURE_PAYMENT_RESULT_STATE_NOT_PASS = "支付响应状态未通过[{}]"

    ROBOT_CHECK = "Robot验证"

    VCC_TYPE_NOT_EXISTENCE = "Vcc类型不存在"
    pass


class ServiceError(MyBaseError):

    def __init__(self, service_state: ServiceStateEnum, *args):
        log = LogUtil(name="ServiceError")
        message = service_state.value.format(*args)
        log.error(message=message, extra={'label': "服务错误"})
        super().__init__(state_enum=service_state, message=message)
