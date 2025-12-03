# 针对OD支付的封装，因已存在的securepay不能拿来使用，因此增加此文件，重新封装
from time import sleep
from urllib.parse import urlencode, urlparse

from pyquery import PyQuery as pq

from common.decorators.retry_decorator import retry_decorator
from common.errors import HttpModuleErrorStateEnum


class Securepay:
    def __init__(self, http_utils, user_agent: str, dest_url: str):
        '''

        Args:
            proxy_info:
            user_agent:
            dest_url: 最后跳转的目标网站，也就是航司网站
        '''

        self.__http_utils = http_utils
        # self.__http_utils.initialize_http_util()
        # self.__http_utils.initialize_http_util(proxy_info=proxy_info)

        self.user_agent = user_agent
        self.timeout = 60
        self.dest_url = dest_url

    def initialize_http_util(self):
        self.__http_utils.initialize_http_util()

    @classmethod
    def get_form_data(cls, form):
        # action = form.attrib["action"]
        action = form.attr("action")
        # print(action)
        inputs = form("input")
        form_data = {}
        for input_tag in inputs.items():
            # input_type = input_tag.attr("type")
            input_name = input_tag.attr("name") or ""
            input_value = input_tag.attr("value") or ""
            if input_name:
                form_data[input_name] = input_value
            # print(f"    Input - Type: {input_type}, Name: {input_name}, Value: {input_value}")
        # print(form_data)

        return action, form_data

    def payment_entrance(self, url, form_data):
        # url = 'https://securepay.e-ghl.com/IPG/Payment.aspx'

        data = urlencode(form_data)

        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Accept-Language": "en",
            "Origin": "null",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Accept-Encoding": "gzip, deflate, br, zstd"
        }
        response_post = self.__http_utils.post(url=url,
                                               data=data,
                                               headers=headers, timeout=self.timeout)
        response_txt = response_post.text

        while '</form>' in response_txt:
            response_txt = response_txt.replace('</html>', '')  # 去掉结束标志，以免获取form出错
            doc = pq(response_txt)
            form = doc("form")  # 目前抓包，网页内只有一个表单
            action, form_data = Securepay.get_form_data(
                form)  # 欺诈返回：'https://booking.batikair.com.my/bookrr_api/api/eghl/return'
            if self.dest_url in action:
                return action, form_data

            data = urlencode(form_data)
            parsed_url = urlparse(action)

            # 获取主机名
            hostname = parsed_url.hostname
            scheme = parsed_url.scheme
            origin = f"{scheme}://{hostname}"
            headers['Host'] = hostname
            headers['Origin'] = origin
            response_post = self.response_mbbmgate(action=action,
                                                   data=data,
                                                   headers=headers)
            response_txt = response_post.text

    @retry_decorator([
        (HttpModuleErrorStateEnum.HTTP_RESULT_TIMEOUT, initialize_http_util),
        (HttpModuleErrorStateEnum.HTTP_UNKNOWN_ABNORMAL, initialize_http_util),
    ])
    def response_mbbmgate(self, action, data, headers):
        """
        执行回调
        Args:
            action:url
            data:数据
            headers:请求头

        Returns:

        """
        sleep(5)
        # #  https://securepay.e-ghl.com/ipg/response_mbbmgate.aspx
        response_post = self.__http_utils.post(url=action,
                                               data=data,
                                               headers=headers, timeout=self.timeout)
        return response_post
