"""
Module: _http_module_error
Author: Ciwei
Date: 2024-09-13

Description: 
    This module provides functionalities for ...
"""

from common.errors._base_state_enum import BaseStateEnum
from common.errors._my_base_error import MyBaseError
from common.utils import CallerInfoUtil


class HttpModuleErrorStateEnum(BaseStateEnum):
    PROXY_INFO_CANNOT_BE_EMPTY = "代理信息不能为空"
    PROXY_SESSION_CANNOT_BE_EMPTY = "代理Session不能为空"
    SET_PROXY_FLIGHT = "设置代理失败：{}"
    HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS = "HTTP响应代码不符合预期[{}],Method[{}]"
    HTTP_RESULT_TIMEOUT = "HTTP响应超时,Method[{}]"
    HTTP_CONNECT_CLOSE = "HTTP连接关闭"
    HTTP_CONNECT_EOF = "EOF错误"
    HTTP_UNKNOWN_ABNORMAL = "HTTP未知异常,Method[{}]"


class HttpModuleError(MyBaseError):
    def __init__(self, http_module_state_enum: HttpModuleErrorStateEnum, *args):

        if http_module_state_enum == HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS:
            if len(args) == 1:
                message = http_module_state_enum.value.format(args[0], CallerInfoUtil.get_caller_name(2))
            else:
                message = http_module_state_enum.value.format(args)
        elif http_module_state_enum in [HttpModuleErrorStateEnum.HTTP_RESULT_TIMEOUT,
                                        HttpModuleErrorStateEnum.HTTP_UNKNOWN_ABNORMAL]:
            message = http_module_state_enum.value.format(CallerInfoUtil.get_caller_name(5))
        else:
            if len(args) == 0:
                message = http_module_state_enum.value
            else:
                message = http_module_state_enum.value.format(args)

        super().__init__(state_enum=http_module_state_enum, message=message)
