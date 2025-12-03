import decimal

from common.decorators.task_decorator import task_decorator
from common.enums import OrderStateEnum
from common.enums import PassengerTypeEnum
from common.errors import ServiceError, ServiceStateEnum
from common.global_variable import GlobalVariable
from common.models import ProxyInfoModel
from common.models.interior_service import JourneyInfoModel, OrderInfoModel
from common.models.task.order import RequestOrderInfoModel
from common.utils import LogUtil
from common.utils.flight_util import FlightUtil
from common.utils.model_conversion_util import ModelConversionUtil
from flights.airchina_ca.services.app_service import AppService

LOG = LogUtil("AirchinaBooking")


@task_decorator(LOG)
def task_main(booking_task_info: RequestOrderInfoModel, response_order: OrderInfoModel):
    proxy_info = ProxyInfoModel.model_validate({
        'host': 'tun-festhu.qg.net',
        'port': 15837,
        'username': '6755776B',
        'password': 'F9800E80653E',
        'region': '',
        'sessTime': '80',
        'userFormatText': '{username}'
    })
    app_service = AppService(proxy_info=None)
    app_service.initialize_http()
    app_service.initialize_token_and_key()
    user = booking_task_info.ext['user']
    password = booking_task_info.ext['password']
    app_service.login(user, password)

    airport_data = [(
        booking_task_info.origin if index == 0 else booking_task_info.destination,
        booking_task_info.destination if index == 0 else booking_task_info.origin,
        booking_task_info.dep_date.strftime("%Y-%m-%d") if index == 0 else booking_task_info.ret_date.strftime(
            "%Y-%m-%d")
    ) for index, value in enumerate(range(2)) if
        index != 1 or (index == 1 and booking_task_info.ret_date is not None)]

    passenger_infos = ModelConversionUtil.api_passenger_to_interior_passenger_model(
        booking_task_info.passenger_list,
        segment_infos=booking_task_info.fare.segment_list,
        purchasing=True
    )
    for i in passenger_infos:
        if '/' not in i.name:
            name = i.name[0] + '/' + i.name[1:]
            i.name = name

    adult_count = sum([1 for x in passenger_infos if x.passenger_type == PassengerTypeEnum.ADT])
    child_count = sum([1 for x in passenger_infos if x.passenger_type == PassengerTypeEnum.CHD])
    private_code = booking_task_info.private_code[0] if booking_task_info.private_code else None
    journey_infos = app_service.search(airport_data=airport_data,
                                       adult_count=adult_count,
                                       child_count=child_count,
                                       currency=booking_task_info.currency,
                                       task_type="booking")
    # 选择航班
    journey_infos = FlightUtil.filtration_flights(journey_infos, flights="^".join(
        [x.flight_number for x in booking_task_info.fare.segment_list]))
    # 查询所有价格
    app_service.fliter(journey_infos, adult_count, child_count)

    flight_info: JourneyInfoModel = FlightUtil.check_flight(flight_data=journey_infos,
                                                            flight_fare=booking_task_info.fare,
                                                            cabin_level=booking_task_info.cabin_level,
                                                            limit_cabin=booking_task_info.ext.get('limitCabin', '0'))
    use_bundle_info = next(
        (x for x in flight_info.bundle_list if x.product_tag == booking_task_info.fare.product_tag))
    select_flight_response, search_response = app_service.select_flight(journey_infos, adult_count, child_count,
                                                                        use_bundle_info)

    # 添加乘机人、联系人
    app_service.add_passenger(passengers_list=passenger_infos,
                              select_flight_response=select_flight_response)

    # 选择乘机人
    search_passenger_list = app_service.select_passenger(passengers_list=passenger_infos,
                                                         select_flight_response=select_flight_response, user=user)

    # 跳转支付页面
    go_pay_response, total_price_amount = app_service.go_pay(select_flight_response=select_flight_response,
                                                             contact_info=booking_task_info.contact_info,
                                                             search_passenger_list=search_passenger_list,
                                                             passenger_infos=passenger_infos, user=user,
                                                             search_response=search_response)
    fare_amount = sum(
        [decimal.Decimal(x.fare) + decimal.Decimal(x.tax) + decimal.Decimal(x.ext.get('oiFee', 0)) for j in
         passenger_infos for x in
         use_bundle_info.price_info if
         x.passenger_type == j.passenger_type])
    if not booking_task_info.need_pay:
        response_order.order_no = go_pay_response['orderId']
        response_order.passengers = passenger_infos
        response_order.bundle_info = use_bundle_info
        response_order.segments = flight_info.segment_list
        response_order.currency = "CNY"
        response_order.order_state = OrderStateEnum.HOLD
        response_order.total_price = fare_amount
    else:
        raise ServiceError(ServiceStateEnum.SERVICE_ERROR, "不支持直接支付，请先生单再走支付接口")
    # 退出登录
    app_service.logout()

    return response_order
