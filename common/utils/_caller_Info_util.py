"""
Module: _caller_Info_util
Author: Ciwei
Date: 2024-10-05

Description:
    调用信息类
"""
import inspect


class CallerInfoUtil:
    @staticmethod
    def get_caller_name(level=1):
        """
            获取调用者的函数名。

            Args:
                level (int): 调用层级，默认是1，表示上一级调用者；2表示上上一级。

            Returns:
                str: 调用者的函数名。
        """
        frame = inspect.stack()[level]
        return frame.function