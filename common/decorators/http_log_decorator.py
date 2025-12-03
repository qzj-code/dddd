"""
Module: _http_decorator
Author: likanghui
Date: 2025-08-23


Description:
    HTTP日志实现
"""
import functools
import json
import time
import traceback
from typing import Optional

from common.global_variable import GlobalVariable
from common.models import ResponseData
from common.utils import LogUtil


def http_log_decorator():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            lob_object = LogUtil("HttpLog")
            start_time = time.time()
            log_data = {
                'url': kwargs['url'],
                'method': func.__name__,
                'headers': kwargs['headers'],
                'data': str(kwargs.get('data')),
                'json': str(kwargs.get('json')),
            }

            if GlobalVariable.OUTPUT_HTTP_LOG:
                lob_object.info(json.dumps(log_data), {"label": "HTTP请求参数"})

            response: Optional[ResponseData] = None

            try:
                response = func(self, *args, **kwargs)
                log_data['responseText'] = response.text
                log_data['responseStatus'] = response.status
                log_data['responseHeaders'] = response.headers
                log_data['time'] = time.time() - start_time
                if GlobalVariable.OUTPUT_HTTP_LOG:
                    lob_object.info(json.dumps(log_data), {"label": "HTTP请求响应"})
            except Exception:
                response = ResponseData(url=kwargs["url"], status=-1)
                log_data["time"] = time.time() - start_time
                log_data["error"] = traceback.format_exc()
                lob_object.info(json.dumps(log_data), {"label": "HTTP请求异常"})

                response.set_error(error=traceback.format_exc())
                raise
            return response

        return wrapper

    return decorator
