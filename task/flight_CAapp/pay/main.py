import datetime

from common.decorators.task_decorator import task_decorator
from common.enums import PayTypeEnum, OrderStateEnum
from common.global_variable import GlobalVariable
from common.models.task.pay import RequestPayInfoModel
from common.utils import LogUtil
from flights.airchina_ca.services.app_service import AppService

_LOG = LogUtil("AirchinaPay")


@task_decorator(_LOG)
def task_main(pay_data: RequestPayInfoModel):
    app_service = AppService(proxy_info=None)
    app_service.initialize_http()
    app_service.initialize_token_and_key()
    user = pay_data.ext['user']
    password = pay_data.ext['password']
    app_service.login(user, password)

    # 支付
    pay_response, serial_number, show_order_prices = app_service.select_order(pay_data.orderNo)
    order_object = {
        "office": pay_data.office,
        "connectOffice": pay_data.connect_office,
        "orderNo": pay_data.orderNo,
        "orderState": OrderStateEnum.OPEN_FOR_USE,
        "currency": "CNY",
        "pnr": pay_data.orderNo,
        "airlinePnr": pay_data.orderNo,
        "payInfo": {
            "payAmount": show_order_prices,
            "payType": PayTypeEnum.VCC,
            "payTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "serialNumber": serial_number
        }
    }
    # 退出登录
    app_service.logout()
    return order_object
