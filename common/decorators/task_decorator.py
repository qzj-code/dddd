"""
Module: _task_decorator
Author: likanghui
Date: 2025-08-23

Description:
    任务处理中间件（优化版：保留结构与对外行为）
"""
import base64
import functools
import gc
import gzip
import hashlib
import inspect
import json
import logging
import time
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Callable

import redis
import requests
from pydantic import ValidationError

from common.enums import TaskTypeEnum, TripTypeEnum, OrderStateEnum
from common.errors import ServiceError, ServiceStateEnum, HttpModuleError, APIError, RiskError
from common.global_variable import GlobalVariable
from common.models.interior_service import OrderInfoModel
from common.models.task import ResponseRootInfoModel
from common.models.task.baggage_search import RequestBagageSearchInfoModel
from common.models.task.cancel import RequestCancelInfoModel
from common.models.task.vcc_model import RequestCreateCardInfoModel, RequestUpdateCardInfoModel, \
    RequestCardAuthorizationInfoModel, RequestDeleteCardInfoModel
from common.models.task.exchangerate import RequestExChangeRateInfoModel
from common.models.task.flight_enrich import RequestFlightEnrichInfoModel
from common.models.task.order import RequestOrderInfoModel, RequestOrderDetailInfoModel
from common.models.task.pay import RequestPayInfoModel
from common.models.task.refund import RequestRefundInfoModel
from common.models.task.register import RequestRegisterFlightModel
from common.models.task.register import ResponsePointsFlightModel
from common.models.task.search import RequestSearchFlightModel, ResponseSearchFlightModel
from common.models.task.search_account import RequestSearchAccountModel
from common.models.task.verify import RequestVerifyPriceModel
from common.utils import LogUtil, flight_util
from common.utils.__log_util import install_logging
from common.utils.order_util import OrderUtil

# ===== 常量 & 工具 =====
_SIGN_SALT = "BgnLccFare!@#"

# 全局复用同一 Redis 连接（基于 ConnectionPool）
_redis_client: Optional[redis.Redis] = None
_redis_pool: Optional[redis.ConnectionPool] = None


def _safe_get(d: Dict, *keys, default=None):
    """安全链式获取"""
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _now_cn_str(fmt: str = "%Y%m%d") -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=8)).strftime(fmt)


def _md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _need_sign(task_type: str) -> bool:
    """这些类型才会注入 sign"""
    return task_type not in [
        TaskTypeEnum.PAY.value,
        TaskTypeEnum.CANCEL.value,
        TaskTypeEnum.EXCHANGE_RATE.value,
        TaskTypeEnum.REFUND.value,
    ]


def _is_async(request_data: Dict) -> bool:
    return bool(_safe_get(request_data, "taskData", "ext", "async", default=False))


def _callback_url(request_data: Dict) -> Optional[str]:
    return _safe_get(request_data, "taskData", "ext", "callbackUrl")


def _build_ok(data: Any, msg: str = "") -> ResponseRootInfoModel:
    return ResponseRootInfoModel.model_validate({
        "code": 0,
        "msg": msg,
        "success": True,
        "data": data
    })


def _build_fail(msg: str, data: Any = None) -> ResponseRootInfoModel:
    return ResponseRootInfoModel.model_validate({
        "code": 1,
        "msg": msg,
        "success": False,
        "data": data
    })


# ===== Redis 工具 =====
def get_redis_client() -> redis.Redis:
    """
    单例 Redis 客户端（ConnectionPool）
    """
    global _redis_client, _redis_pool
    if _redis_client is None:
        _redis_pool = redis.ConnectionPool(
            host=GlobalVariable.REDIS_HOST,
            port=GlobalVariable.REDIS_PORT,
            db=GlobalVariable.REDIS_TASK_RESULT_DB,
            password=GlobalVariable.REDIS_PASSWORD,
            decode_responses=True,
            socket_keepalive=True,
            socket_timeout=5,
            max_connections=128
        )
        _redis_client = redis.StrictRedis(connection_pool=_redis_pool, decode_responses=True)
    return _redis_client


def increment_ride_flow_count(key: str, expire_seconds: int = 48 * 3600) -> int:
    """
    计数 + 确保过期时间存在
    """
    client = get_redis_client()
    pipe = client.pipeline()
    pipe.incr(key)
    pipe.ttl(key)
    new_value, ttl = pipe.execute()

    # -2: 不存在；-1: 存在但无过期
    if ttl < 0:
        client.expire(key, expire_seconds)

    return int(new_value)


# ===== 业务小函数 =====
def call_url(log_object: LogUtil, url: str, data_json: str):
    """
    异步回调：GZIP + Base64
    """
    try:
        headers = {
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Encoding": "gzip"
        }
        log_object.info("回调开始")
        log_object.info(data_json, {"label": "回调数据"})

        compressed = gzip.compress(data_json.encode("utf-8"))
        encoded = base64.b64encode(compressed).decode("utf-8")

        resp = requests.post(url, data=encoded, headers=headers, timeout=30)
        log_object.info(resp.text, {"label": "回调响应"})
    except Exception:
        log_object.info(data_json, {"label": "回调异常数据"})
        log_object.error(traceback.format_exc(), {"label": "回调异常"})


def store_pnr_cache(log_object: LogUtil, record: Dict):
    """
    将 PNR 记录存入 Redis 缓存（Hash）
    """
    redis_client = get_redis_client()
    hash_key = f"GDS_PNR_RECORD:{record['dataSource']}"
    row_key = record["pnr"] or record.get("airlinePnr", "")
    payload = json.dumps(record, ensure_ascii=False)

    log_object.info(f"{hash_key}:{row_key}:{payload}", {"label": "存入缓存数据"})
    ret = redis_client.hset(hash_key, row_key, payload)
    if ret == 1:
        log_object.info("存入缓存成功", {"label": "存入缓存结果"})
    else:
        log_object.error("存入缓存失败", {"label": "存入缓存结果"})


def emit(log_object, payload: dict):
    try:
        log_object.info("发送日志")

        resp = requests.post('http://47.116.13.161:9309/exteriorLog/add', json=payload, timeout=30)
        log_object.info(resp.text, {"label": "日志响应"})
    except Exception:
        log_object.error(traceback.format_exc(), {"label": "发送日志异常"})


def _build_search_response(request_data: Dict, fare_list: list) -> ResponseSearchFlightModel:
    """统一构建查询/验价响应体"""
    td = request_data.get("taskData", {})
    session_id = td.get("sessionId", "")
    ret_date = td.get("retDate")
    trip_type = TripTypeEnum.ONE_WAY if not ret_date else TripTypeEnum.ROUND_TRIP
    return ResponseSearchFlightModel.model_validate({
        "sign": "",
        "sessionId": session_id,
        "tripType": trip_type,
        "fareList": fare_list or []
    })


def _build_error_payload_for_type(task_data: Dict, task_type: str,
                                  order_data: Optional[OrderInfoModel] = None) -> Any:
    """不同 taskType 的 data 兜底结构"""
    td = task_data.get("taskData", {})
    session_id = td.get("sessionId", "")

    if task_type in [TaskTypeEnum.SEARCH.value, TaskTypeEnum.VERIFY.value]:
        return ResponseSearchFlightModel.model_validate({
            "sign": "",
            "sessionId": session_id,
            "tripType": TripTypeEnum.ONE_WAY if not td.get("retDate") else TripTypeEnum.ROUND_TRIP,
            "fareList": []
        })

    if task_type in [TaskTypeEnum.BOOKING.value, TaskTypeEnum.ORDER_DETAIL.value]:
        if order_data:
            # 只要有 PNR/订单号，即认为 HOLD，但 code 仍由上层决定
            if order_data.pnr or order_data.order_no:
                order_data.order_state = order_data.order_state or OrderStateEnum.HOLD
            else:
                order_data.order_state = order_data.order_state or OrderStateEnum.ABNORMAL
            return OrderUtil.order_info_to_request_order_info(order_data, session_id)

    if task_type in [TaskTypeEnum.REGISTER.value, TaskTypeEnum.SEARCH_ACCOUNT.value, TaskTypeEnum.EXCHANGE.value]:
        return ResponsePointsFlightModel.model_validate({
            "sign": "",
            "sessionId": session_id,
        })

    return None


def task_decorator(log_object: LogUtil):
    """
    装饰器
    """

    def task_search(func: Callable, task_data: RequestSearchFlightModel):
        resp = func(task_data, TaskTypeEnum.SEARCH)
        resp = flight_util.FlightUtil.filtration_carrier(resp, task_data.carrier)
        resp = flight_util.FlightUtil.filtration_cabin_level(resp, task_data.cabin_level)
        resp = flight_util.FlightUtil.filtration_max_connection(resp, task_data.max_connection)
        resp = flight_util.FlightUtil.journey_infos_to_fare_data(
            resp,
            data_source=task_data.data_source,
            connect_office=task_data.connect_office,
            office=task_data.office,
            passenger_count=task_data.adult_number + task_data.child_number,
            private_code=(task_data.private_code[0] if task_data.private_code else "")
        )
        resp = flight_util.FlightUtil.check_passenger_type(resp, task_data.adult_number, task_data.child_number)
        if not resp:
            raise ServiceError(ServiceStateEnum.NO_FLIGHT_DATA)
        return resp

    def task_verify(func: Callable, task_data: RequestVerifyPriceModel):
        resp = func(task_data, TaskTypeEnum.VERIFY)
        resp = flight_util.FlightUtil.filtration_flights(
            resp,
            flights="^".join([x.flight_number for x in task_data.segment_list])
        )
        resp = flight_util.FlightUtil.journey_infos_to_fare_data(
            resp,
            data_source=task_data.data_source,
            connect_office=task_data.connect_office,
            office=task_data.office,
            passenger_count=task_data.adult_number + task_data.child_number,
            private_code=(task_data.private_code[0] if task_data.private_code else "")
        )
        resp = flight_util.FlightUtil.check_passenger_type(resp, task_data.adult_number, task_data.child_number)
        if not resp:
            raise ServiceError(ServiceStateEnum.NO_FLIGHT_DATA)
        return resp

    def task_booking(func: Callable, task_data: RequestOrderInfoModel, order_data: OrderInfoModel):
        return func(task_data, order_data)

    def task_order_detail(func: Callable, task_data: RequestOrderDetailInfoModel):
        return func(task_data)

    def task_baggage_search(func: Callable, task_data: RequestBagageSearchInfoModel):
        return func(task_data)

    def task_register(func: Callable, task_data: RequestRegisterFlightModel):
        return func(task_data)

    def task_search_account(func: Callable, task_data: RequestSearchAccountModel):
        return func(task_data)

    def task_pay(func: Callable, task_data: RequestPayInfoModel):
        return func(task_data)

    def task_cancel(func: Callable, task_data: RequestCancelInfoModel):
        return func(task_data)

    def task_refund(func: Callable, task_data: RequestRefundInfoModel):
        return func(task_data)

    def task_exchange_rate(func: Callable, task_data: RequestExChangeRateInfoModel):
        return func(task_data)

    def exchange(func: Callable, task_data: RequestRegisterFlightModel):
        return func(task_data)

    def flight_enrich(func: Callable, task_data: RequestFlightEnrichInfoModel):
        return func(task_data)

    def create_card(func: Callable, task_data: RequestCreateCardInfoModel):
        return func(task_data)

    def update_card(func: Callable, task_data: RequestUpdateCardInfoModel):
        return func(task_data)

    def authorization_card(func: Callable, task_data: RequestCardAuthorizationInfoModel):
        return func(task_data)

    def delete_card(func: Callable, task_data: RequestDeleteCardInfoModel):
        return func(task_data)

    def traffic(func: Callable, task_data):
        return func(task_data)

    def authorization_notification(func: Callable, task_data):
        return func(task_data)

    def build_error(task_data: Dict, message: str,
                    order_data: Optional[OrderInfoModel] = None) -> ResponseRootInfoModel:
        task_type = task_data.get("taskType", "")
        data = _build_error_payload_for_type(task_data, task_type, order_data)
        code = 1

        if task_type in [TaskTypeEnum.BOOKING.value, TaskTypeEnum.ORDER_DETAIL.value]:
            if isinstance(data, dict) or data is not None:
                if isinstance(order_data, OrderInfoModel) and (order_data.pnr or order_data.order_no):
                    code = 0

        return ResponseRootInfoModel.model_validate({
            "code": code,
            "msg": message,
            "success": (code == 0),
            "data": data
        })

    # === 主装饰器 ===
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取调用者（上一层栈帧）
            caller_frame = inspect.stack()[1]
            caller_name = caller_frame.function
            start_ts = time.time()
            # 默认失败体
            result_data = _build_fail(ServiceStateEnum.INTERNAL_ERROR.value)
            try:
                request_data: Dict = args[0]  # 与现有业务一致：第一个参数为 dict
                request_data: Dict = {
                    "taskData": request_data,
                    "taskId": request_data['sessionId'],
                    "taskType": caller_name
                }
                task_id = request_data.get("taskId", "")
                task_type = request_data.get("taskType", "")
                data_source = request_data['taskData'].get("dataSource", "")
                PROJECT_ROOT = Path(__file__).resolve().parents[2]
                LOG_DIR = PROJECT_ROOT / "logs" / data_source
                install_logging(
                    base_dir=str(LOG_DIR),
                    prefix=f"{data_source}-",
                    when="D",
                    backup_count=7,
                    console=True,
                    level=logging.INFO,
                )
                log_object.set_log_type(task_type)
                log_object.set_options({"options": {"taskId": task_id}})

                # 任务过期快速返回
                task_expire_ms = request_data.get("taskExpireTime")
                if task_expire_ms and int(time.time() * 1000) > int(task_expire_ms):
                    log_object.info("任务过期！", {"label": "任务状态"})
                    return None

                log_object.info(json.dumps(request_data), {"label": "任务参数"})

                order_data = OrderInfoModel()
                td = request_data.get("taskData", {})
                session_id = td.get("sessionId", "")

                try:
                    response = None
                    message = ""
                    # === 分发 ===
                    if task_type in [TaskTypeEnum.SEARCH.value, TaskTypeEnum.VERIFY.value]:
                        if task_type == TaskTypeEnum.SEARCH.value:
                            model = RequestSearchFlightModel.model_validate(td)
                            fare_list = task_search(func, model)
                            message = ServiceStateEnum.SEARCH_FLIGHT_DATA_SUCCESS.value
                        else:
                            model = RequestVerifyPriceModel.model_validate(td)
                            fare_list = task_verify(func, model)
                            message = ServiceStateEnum.VERIFY_FLIGHT_DATA_SUCCESS.value

                        response = _build_search_response(request_data, fare_list)

                    elif task_type == TaskTypeEnum.BOOKING.value:
                        model = RequestOrderInfoModel.model_validate(td)

                        order_data = task_booking(func, model, order_data)
                        message = ServiceStateEnum.ORDER_FLIGHT_DATA_SUCCESS.value
                        response = OrderUtil.order_info_to_request_order_info(order_data, session_id)

                        # 白名单：缓存PNR
                        if model.fare.data_source in GlobalVariable.PNR_CACHE_WHITELIST:
                            store_pnr_cache(log_object, {
                                "airlinePnr": order_data.pnr,
                                "connectOffice": model.connect_office,
                                "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "dataSource": model.fare.data_source,
                                "ndcOrderId": "",
                                "office": model.office,
                                "orderOwnerCode": "",
                                "pnr": order_data.pnr,
                                "sessionId": model.session_id,
                                "contactInfo": td.get("contactInfo")
                            })

                    elif task_type == TaskTypeEnum.ORDER_DETAIL.value:
                        model = RequestOrderDetailInfoModel.model_validate(td)
                        od = task_order_detail(func, model)
                        message = ServiceStateEnum.SEARCH_ORDER_DETAIL_SUCCESS.value
                        response = OrderUtil.order_info_to_request_order_info(od, session_id)

                    elif task_type == TaskTypeEnum.PAY.value:
                        model = RequestPayInfoModel.model_validate(td)
                        response = task_pay(func, model)
                        message = ServiceStateEnum.BOOKING_PAYMENT_SUCCESS.value

                    elif task_type == TaskTypeEnum.CANCEL.value:
                        model = RequestCancelInfoModel.model_validate(td)
                        response = task_cancel(func, model)
                        message = ServiceStateEnum.BOOKING_CANCEL_SUCCESS.value

                    elif task_type == TaskTypeEnum.EXCHANGE_RATE.value:
                        model = RequestExChangeRateInfoModel.model_validate(td)
                        response = task_exchange_rate(func, model)  # 修正
                        message = ServiceStateEnum.SEARCH_EXCHANGERATE_SUCCESS.value

                    elif task_type == TaskTypeEnum.REFUND.value:
                        model = RequestRefundInfoModel.model_validate(td)
                        response = task_refund(func, model)
                        message = ServiceStateEnum.BOOKING_REFUND_SUCCESS.value

                    elif task_type == TaskTypeEnum.BAGGAGE_SEARCH.value:
                        model = RequestBagageSearchInfoModel.model_validate(td)
                        response = task_baggage_search(func, model)
                        message = ServiceStateEnum.SEARCH_BAGGAGE_DATA_SUCCESS.value

                    elif task_type == TaskTypeEnum.REGISTER.value:
                        model = RequestRegisterFlightModel.model_validate(td)
                        response = task_register(func, model)
                        message = ServiceStateEnum.REGISTER_SUCCESS.value

                    elif task_type == TaskTypeEnum.SEARCH_ACCOUNT.value:
                        model = RequestSearchAccountModel.model_validate(td)
                        response = task_search_account(func, model)
                        message = ServiceStateEnum.SEARCH_ACCOUNT_SUCCESS.value

                    elif task_type == TaskTypeEnum.EXCHANGE.value:
                        model = RequestRegisterFlightModel.model_validate(td)
                        response = exchange(func, model)
                        message = ServiceStateEnum.EXCHANGE_SUCCESS.value
                    elif task_type == TaskTypeEnum.FLIGHT_ENRICH.value:
                        model = RequestFlightEnrichInfoModel.model_validate(td)
                        response = flight_enrich(func, model)
                        message = '成功'
                    elif task_type == TaskTypeEnum.CREATE_CARD.value:
                        model = RequestCreateCardInfoModel.model_validate(td)
                        response = create_card(func, model)
                        message = '创建卡成功'
                    elif task_type == TaskTypeEnum.UPDATE_CARD.value:
                        model = RequestUpdateCardInfoModel.model_validate(td)
                        response = update_card(func, model)
                        message = '更新卡成功'
                    elif task_type == TaskTypeEnum.SEARCH_AUTHORIZATION.value:
                        model = RequestCardAuthorizationInfoModel.model_validate(td)
                        response = authorization_card(func, model)
                        message = '查询授权成功'
                    elif task_type == TaskTypeEnum.DELETE_CARD.value:
                        model = RequestDeleteCardInfoModel.model_validate(td)
                        response = delete_card(func, model)
                        message = '注销成功'
                    elif task_type == TaskTypeEnum.TRAFFIC.value:
                        response = traffic(func, td)
                        message = '查询流量成功'
                    elif task_type == TaskTypeEnum.NOTIFICATION_AUTHORIZATION.value:
                        response = authorization_notification(func, td)
                        message = '接收成功'
                    # 成功包裹
                    result_data = _build_ok(response, message)

                except HttpModuleError as e:
                    result_data = build_error(request_data, e.message, order_data)
                    log_object.error(traceback.format_exc(), {"label": "HTTP错误"})

                except ServiceError as e:
                    # 特判：票号信息错误 -> 返回成功但异常态订单
                    if getattr(e, "code", None) in [
                        getattr(ServiceStateEnum, "TICKET_NUMBER_INFO_MISTAKE", None).name if hasattr(ServiceStateEnum,
                                                                                                      "TICKET_NUMBER_INFO_MISTAKE") else None]:
                        order_data.order_state = OrderStateEnum.ABNORMAL
                        result_data = _build_ok(
                            OrderUtil.order_info_to_request_order_info(order_data, session_id),
                            e.message
                        )
                    else:
                        result_data = build_error(request_data, e.message, order_data)
                        log_object.error(traceback.format_exc(), {"label": "服务错误"})
                        # 无航班也视为成功（兼容原行为）
                        if (getattr(e, "code", None) in [ServiceStateEnum.NO_FLIGHT_DATA.name]
                                and request_data.get("taskType") == TaskTypeEnum.SEARCH.value):
                            result_data.code = 0
                            result_data.success = True

                except ValidationError as e:
                    # 取第一个错误更友好；并保底兜底信息
                    try:
                        error_json = json.loads(e.json())
                        first = error_json[0] if error_json else {}
                        loc = first.get("loc", [])
                        msg = first.get("msg", "Validation error")
                        message = f'{loc[0]} {msg}' if loc else msg
                    except Exception:
                        message = "Validation error"
                    result_data = build_error(request_data, message, order_data)
                    log_object.error(traceback.format_exc(), {"label": "验证错误"})

                except APIError as e:
                    result_data = build_error(request_data, e.message, order_data)
                    log_object.error(traceback.format_exc(), {"label": "第三方接口错误"})

                except RiskError as e:
                    result_data = build_error(request_data, e.message, order_data)
                    log_object.error(traceback.format_exc(), {"label": "风控错误"})

                except Exception:
                    result_data = build_error(request_data, "系统异常", order_data)
                    log_object.error(traceback.format_exc(), {"label": "内部错误"})

                # 注入签名
                if _need_sign(request_data.get("taskType", "")) and result_data.data is not None:
                    sid = _safe_get(request_data, "taskData", "sessionId", default="")
                    sign_md5 = _md5_hex(f"{sid}{_SIGN_SALT}")
                    # 注意：SEARCH/VERIFY 的 data 一定是带 sign 字段的模型；其余类型也按原行为注入
                    try:
                        result_data.data.sign = sign_md5
                    except Exception:
                        # 兼容：若 data 非 pydantic 模型，尝试 dict 注入
                        if isinstance(result_data.data, dict):
                            result_data.data["sign"] = sign_md5

                # 异步回调
                if _is_async(request_data):
                    cb = _callback_url(request_data)
                    if cb:
                        call_url(log_object, cb, result_data.model_dump_json(by_alias=True))
                if task_type not in [TaskTypeEnum.FLIGHT_ENRICH.value]:
                    # 成功统计埋点（白名单）
                    if result_data.code == 0:
                        today = _now_cn_str("%Y%m%d")
                        ds = _safe_get(request_data, "taskData", "dataSource", default="")
                        office = _safe_get(request_data, "taskData", "office", default="")
                        tt = request_data.get("taskType", "").upper()
                        rides_key = f"GDS_FLOW_COUNT:{today}:{ds}|{office}|{tt}"
                        cnt = increment_ride_flow_count(rides_key)
                        log_object.info(f"rides_key={rides_key} count={cnt}", {"label": "埋点"})

                    emit(log_object=log_object, payload={
                        "consumeTime": int(time.time() - start_ts),  # 耗时
                        "dataSource": td.get("dataSource", ""),  # 数据源
                        "interfaceName": task_type,  # 接口名称
                        "resultMessage": '成功' if result_data.code == 0 else '异常',  # 结果
                        "sessionId": td.get("orderSessionId", td.get("sessionId", "")),  # sessionId
                        "office": td.get("office", ""),  # office
                        "status": result_data.code,
                        "requestMsg": json.dumps(request_data, default=str),  # 请求
                        "responseMsg": result_data.model_dump_json(by_alias=True),  # 响应
                    })

                # 收尾
                gc.collect()
                log_object.info(result_data.model_dump_json(by_alias=True), {"label": "任务结果"})
                log_object.info(f"{time.time() - start_ts:.2f}", {"label": "任务耗时"})

                return json.loads(result_data.model_dump_json(by_alias=True))

            except Exception:
                log_object.error(traceback.format_exc(), {"label": "全局系统异常"})

        return wrapper

    return decorator
