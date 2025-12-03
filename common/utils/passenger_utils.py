"""
@Project     : flights
@Author      : likanghui
@Date        : 2024/10/15 14:26
@Description :
@versions    : 1.0.0.0
"""
import copy
import decimal
from datetime import datetime
from typing import List

from common.models.task._passenger_info_model import PassengerInfoModel


class PassengerUtils:
    @classmethod
    def age_compute_month(cls, date_of_birth):
        birthdate = datetime.strptime(date_of_birth, "%Y-%m-%d")
        today = datetime.today()
        # Directly calculate the difference in years
        age = today.year - birthdate.year
        return age

    @classmethod
    def age_compute_year(cls, date_of_birth):
        # 将字符串格式的出生日期转换为datetime对象
        birthdate = datetime.strptime(date_of_birth, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - birthdate.year
        return age

    @classmethod
    def age_compute(cls, dep_date, date_of_birth):
        """
        计算年龄
        :param date_of_birth:
        :return:
        """
        birthdate_datetime = datetime.strptime(date_of_birth, '%Y-%m-%d')
        today = datetime.strptime(dep_date, "%Y-%m-%d")

        age = today.year - birthdate_datetime.year - (
                (today.month, today.day) < (birthdate_datetime.month, birthdate_datetime.day))
        return age

    @classmethod
    def get_passenger_sum_number(cls,
                                 passenger_data: List[PassengerInfoModel],
                                 passenger_map: dict) -> dict:
        """
        统计乘客数据中各种类型乘客的数量。

        该方法接收一个乘客数据列表和一个乘客类型映射字典，返回一个更新后的字典，
        其中包含各种乘客类型的数量统计。

        @param passenger_data: 乘客信息列表，每个元素是一个 PassengerInfoModel 实例。
        @param passenger_map: 乘客类型映射字典，键是乘客类型，值是初始数量。
        @return: 更新后的字典，包含各种乘客类型的数量统计。
        """

        # 深拷贝乘客映射字典，以确保不修改原始数据
        result_map = copy.deepcopy(passenger_map)

        for i in passenger_data:
            # 如果乘客类型在字典中不存在，则初始化为1；否则，数量加1
            result_map[i.passenger_type] = result_map.get(i.passenger_type, 0) + 1

        return result_map
