"""
Module: _order_type_enum.py
Author: Ciwei
Date: 2024-10-19

Description:
    订单状态
"""
from enum import Enum


class OrderStateEnum(Enum):
    HOLD = "HOLD"  # 等待支付
    OPEN_FOR_USE = "OPEN FOR USE"  # 等待使用
    REFUND = "REFUND"  # 退票
    USED = "USED"  # 已使用
    UNKNOWN = "UNKNOWN"  # 未知
    ABNORMAL = "ABNORMAL"  # 异常
    CHECKED_IN = "CHECKED IN"  # 值机
    CANCEL = "CANCEL" # 取消
