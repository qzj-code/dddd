"""
Module: _task_type_enum
Author: Ciwei
Date: 2024-09-13

Description:
    任务类型模型
"""
from enum import Enum


class TaskTypeEnum(Enum):
    SEARCH = 'search'  # 查询
    VERIFY = 'verify'  # 验价
    BOOKING = 'booking'  # 生单
    ORDER_DETAIL = 'order_detail'  # 订单详情
    PAY = 'pay'
    CANCEL = 'cancel'
    EXCHANGE_RATE = 'exchange_rate'
    REFUND = 'refund'
    BAGGAGE_SEARCH = 'baggage_search'
    REGISTER = "register"  # 积分注册接口
    SEARCH_ACCOUNT = 'search_account'  # 查询账户接口
    EXCHANGE = 'exchange'
    FLIGHT_ENRICH = 'flight_enrich'
    CREATE_CARD = 'create_card'  # 创建VCC卡
    UPDATE_CARD = 'update_card'
    TRAFFIC = 'traffic'  # 流量
    SEARCH_AUTHORIZATION = 'card_authorization'
    DELETE_CARD = 'delete_card'
    NOTIFICATION_AUTHORIZATION='authorization_notification'
