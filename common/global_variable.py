"""
@Project     : zhongyi_flight
@Author      : ciwei
@Date        : 2024/6/27 14:51 
@Description : 
@versions    : 1.0.0.0
"""
import os

from common.models import ProxyInfoModel

# 初始化环境变量
_ENV_STRING = os.environ.get("ENV", "DEV")

if _ENV_STRING == "DEV":
    os.environ.setdefault("REDIS_HOST", 'r-uf6nd278tkrd5skpncpd.redis.rds.aliyuncs.com')
    os.environ.setdefault("REDIS_PORT", '6379')
    os.environ.setdefault("REDIS_USERNAME", '')
    os.environ.setdefault("REDIS_PASSWORD", 'ky202488A1!@#')
    os.environ.setdefault("OUTPUT_HTTP_LOG", 'true')

    # os.environ.setdefault("REDIS_HOST", '47.116.169.153')
    # os.environ.setdefault("REDIS_PORT", '6379')
    # os.environ.setdefault("REDIS_USERNAME", '')
    # os.environ.setdefault("REDIS_PASSWORD", 'bgn2024qwe')
    # os.environ.setdefault("OUTPUT_HTTP_LOG", 'true')
    os.environ.setdefault("PROXY_HOST", '127.0.0.1')
    os.environ.setdefault("PROXY_PORT", '9000')
    os.environ.setdefault("PROXY_USERNAME", '')
    os.environ.setdefault("PROXY_PASSWORD", '')
    os.environ.setdefault("userFormatText", '')

if _ENV_STRING == "PROD":
    os.environ.setdefault("REDIS_HOST", 'r-uf6nd278tkrd5skpncpd.redis.rds.aliyuncs.com')
    os.environ.setdefault("REDIS_PORT", '6379')
    os.environ.setdefault("REDIS_USERNAME", '')
    os.environ.setdefault("REDIS_PASSWORD", 'ky202488A1!@#')
    os.environ.setdefault("OUTPUT_HTTP_LOG", 'true')


class GlobalVariable:
    PROXY = ProxyInfoModel.model_validate({
        'host': os.environ.get('PROXY_HOST', 'zjdanli007.pr-as.roxlabs.cn'),
        'port': int(os.environ.get('PROXY_PORT', '4600')),
        'username': os.environ.get('PROXY_USERNAME', 'test009'),
        'password': os.environ.get('PROXY_PASSWORD', 'test009'),
        'region': os.environ.get('PROXY_REGION', 'hk'),
        'sessTime': int(os.environ.get('PROXY_SESS_TIME', '10')),
        'userFormatText': os.environ.get('PROXY_USER_FORMAT_TEXT',
                                         'user-{username}-region-{region}-sessid-{session}-sesstime-{sess_time}-keep-true')
    })

    ENV = _ENV_STRING  # 环境变量
    REDIS_HOST = os.environ.get("REDIS_HOST")  # redis host
    REDIS_PORT = int(os.environ.get("REDIS_PORT"))  # redis port
    REDIS_TASK_RESULT_DB = 0
    REDIS_USERNAME = os.environ.get("REDIS_USERNAME")
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")  # redis password

    PROXY_HOST = "host"  # proxy_host 键
    PROXY_PORT = "port"  # proxy_port 键
    PROXY_USERNAME = "username"  # proxy_username 键
    PROXY_PASSWORD = "password"  # proxy_password 键

    RABBITMQ_USERNAME = os.environ.get('RABBITMQ_USERNAME')
    RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD')
    RECORD_API_LIST = ['UOapi']
    OUTPUT_HTTP_LOG = True if os.environ.get('OUTPUT_HTTP_LOG', 'false') == 'true' else False
    PNR_CACHE_WHITELIST = ['UOagent', 'FZagent']
