"""
Module: main
Author: Ciwei
Date: 2024-10-24

Description:
    This module provides functionalities for ...
"""
import decimal

from common.decorators.task_decorator import task_decorator
from common.enums import TaskTypeEnum
from common.global_variable import GlobalVariable
from common.models import ProxyInfoModel
from common.models.task.search import RequestSearchFlightModel
from common.utils import LogUtil, MachineCache, flight_util
from flights.airchina_ca.services.app_service import AppService

LOG = LogUtil("AirchinaSearch")
CACHE = MachineCache()


@task_decorator(LOG)
def task_main(search_task_info: RequestSearchFlightModel, task_type: TaskTypeEnum):
    script_cache = CACHE.get_data()
    if script_cache is None:
        proxy_info = ProxyInfoModel.model_validate({
            'host': 'tun-festhu.qg.net',
            'port': 15837,
            'username': '6755776B',
            'password': 'F9800E80653E',
            'region': '',
            'userFormatText': '{username}',
            'sessTime': '80',
        })
        app_service = AppService(proxy_info=proxy_info)
        app_service.initialize_http()
        app_service.initialize_token_and_key()
        user = search_task_info.ext.user
        password = search_task_info.ext.password
        # if user:
        #     app_service.login(user, password)
    else:
        app_service = script_cache['value']
    airport_data = [(
        search_task_info.origin if index == 0 else search_task_info.destination,
        search_task_info.destination if index == 0 else search_task_info.origin,
        search_task_info.dep_date.strftime("%Y-%m-%d") if index == 0 else search_task_info.ret_date.strftime("%Y-%m-%d")
    ) for index, value in enumerate(range(2)) if
        index != 1 or (index == 1 and search_task_info.ret_date is not None)]

    journeys = app_service.search(airport_data=airport_data,
                                  adult_count=search_task_info.adult_number,
                                  child_count=search_task_info.child_number,
                                  currency=search_task_info.currency)
    if task_type.value == 'search':
        app_service.fliter(journeys, search_task_info.adult_number, search_task_info.child_number,
                           task_type="search")
    else:
        response = flight_util.FlightUtil.filtration_flights(journeys, flights="^".join(
            [x.flight_number for x in search_task_info.segment_list]))
        app_service.fliter(response, search_task_info.adult_number, search_task_info.child_number)

    # redis获取税费
    redis_tax_response = app_service.redis_tax(search_task_info.origin, search_task_info.destination)
    if not redis_tax_response:
        # redis没有渠道改航线的税费
        redis_tax_response = app_service.get_tax(journeys, search_task_info.adult_number,
                                                 search_task_info.child_number)
        app_service.add_redis_tax(redis_tax_response)
    for journey in journeys:
        for i in journey.bundle_list:
            for j in i.price_info:
                if not redis_tax_response.get(j.passenger_type.value):
                    continue
                j.tax = decimal.Decimal(redis_tax_response.get(j.passenger_type.value).get('tax'))
                j.ext['oiFee'] = decimal.Decimal(redis_tax_response.get(j.passenger_type.value).get('oifee', 0))

    if script_cache is None:
        CACHE.set_data(app_service, 480)
    else:
        CACHE.set_data(script_cache['value'], None, script_cache['timeOut'])
    return journeys
