"""
Module: _pay_type_enum
Author: likanghui
Date: 2024-10-15

Description:
    支付方式枚举
"""
from enum import Enum


class PayTypeEnum(Enum):
    VCC = "VCC"  # 信用卡
    CASH = "CASH"  # 现金
    DPAY = "DPAY"  # 德付通
    COUPON = "COUPON"  # 代金券
    YEEPAY = "YEEPAY" # 易宝支付
    ALIPAY = "ALIPAY"  # 支付宝
    WECHATPAY = "WECHATPAY"  # 微信支付
