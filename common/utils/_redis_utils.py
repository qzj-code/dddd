"""
Module: _redis_utils
Author: Ciwei
Date: 2025-02-09

Description: 
    This module provides functionalities for ...
"""
import redis


class RedisUtils:
    """
    Redis Utils基础类
    """

    def __init__(self, host: str, port: int = 6379, db: int = 0):
        self.__pool = redis.ConnectionPool(host=host, port=port, db=db)

    def __get_client(self):
        return redis.Redis(connection_pool=self.__pool)

    def get(self, key):
        redis_client = self.__get_client()
        return redis_client.get(key)

    def set(self, key, value, expire=60):
        redis_client = self.__get_client()
        return redis_client.set(key, value, ex=expire)

    def expire(self, key, expire=60):
        redis_client = self.__get_client()
        return redis_client.expire(key, time=expire)
