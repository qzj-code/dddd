import time
import urllib.parse

from bs4 import BeautifulSoup

from common.errors import HttpModuleError, HttpModuleErrorStateEnum
from common.utils.http_utils import TlsClientHttpUtil


class Yeepay:
    def __init__(self):

        self.__http_utils = TlsClientHttpUtil()
        self.__http_utils.initialize_http_util()
        self.__timeout = 60

    def bcnewpc_request(self, url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        response = self.__http_utils.get(url=url, headers=headers)
        if response.status != 302 and response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response

    def pay_post_action(self, url, data):
        """
        https://www.yeepay.com/app-airsupport/AirSupportService.action
        Args:
            url:
            data:

        Returns:

        """
        headers = {
            "Host": "www.yeepay.com",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://easypay.travelsky.com.cn",
            "Connection": "keep-alive",
            "Referer": "https://easypay.travelsky.com.cn/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.post(url=url, headers=headers, data=urllib.parse.urlencode(data))
        if response.status != 302:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        # "https://cashdesk.yeepay.com/bc-cashier/bcnewpc/request/10012428626/2125021007273423"
        return response.location

    def pay(self, url, referer):
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Pragma': 'no-cache',
            'Referer': referer,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        response = self.__http_utils.get(url=url, headers=headers)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def airlinepay(self, url: str, referer: str):
        """
        获取易宝支付表单数据
        https://easypay.travelsky.com.cn/easypay/airlinepay.servlet?OrderAmount=420&AppType=B2C&BankId=YEEPAYSHARE&BillNo=2125021007273423&Ext1=&Ext2=&Lan=CN&Msg=SuperPNR_ID%3D202502101007415877&OrderCurtype=CNY&OrderNo=202502101008501622&OrderType=1%7C0%7C&OrgId=KNAIR&OrderDate=20250210&OrderTime=100745&ordername=KN-ETICKET&Orderinfo=&usrid=&username=&gateid=&Version=1.0&ReturnId=id_kn_paynew&SIGNATURE=5c27ec37c10b7c0a50f9cd32acd06b24
        Args:
            referer:
            url:

        Returns:

        """
        headers = {
            "Host": "easypay.travelsky.com.cn",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": referer,  # "https://www.flycua.com/payment/202502101007415877",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.get(url=url, headers=headers)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def querystate(self, customer_no: str, customer_request_no: str):
        """
        支付成功后回调第一部
        Args:
            customer_no:
            customer_request_no:

        Returns:

        """
        headers = {
            "Host": "cashdesk.yeepay.com",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Connection": "keep-alive",
            "Referer": f"https://cashdesk.yeepay.com/bc-cashier/bcnewpc/request/{customer_no}/{customer_request_no}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        response = self.__http_utils.get(
            url=f"https://cashdesk.yeepay.com/bc-cashier/bcnewpc/result/querystate?customerNo={customer_no}&customerRequestNo={customer_request_no}&times={int(time.time() * 1000)}",
            headers=headers)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def query_result(self, url: str, customer_no: str, customer_request_no: str):
        """

        Args:
            url:
            customer_no:
            customer_request_no:

        Returns:

        """
        headers = {
            "Host": "cashdesk.yeepay.com",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Connection": "keep-alive",
            "Referer": f"https://cashdesk.yeepay.com/bc-cashier/bcnewpc/request/{customer_no}/{customer_request_no}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        response = self.__http_utils.get(
            url=f"https://cashdesk.yeepay.com/bc-cashier/bcnewpc{url}?customerNo={customer_no}&customerRequestNo={customer_request_no}&times={int(time.time() * 1000)}",
            headers=headers)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.json

    def pay_success(self, url):
        """
        支付回调

        Args:
            url:https://cashdesk.yeepay.com/bc-cashier/bcnewpc/pay/success/10012428626/2125021007273731

        Returns:

        """
        headers = {
            "Host": "cashdesk.yeepay.com",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.get(
            url=url,
            headers=headers, auth_redirect=True)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找具有特定类名的 <a> 标签
        button_element = soup.find('a', class_='button back-merchant none')
        url = button_element.get('href')
        return url

    def callback(self, url):
        """

        Args:
            url:

        Returns:

        """
        headers = {
            "Host": "easypay.travelsky.com.cn",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.get(
            url=url,
            headers=headers)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取 form 的 action 属性
        form_action = soup.find('form')['action']

        # 提取所有 hidden 输入字段
        hidden_inputs = soup.find_all('input', type='hidden')

        # 获取每个 hidden input 的 name 和 value
        form_data = {input_tag['name']: input_tag['value'] for input_tag in hidden_inputs}
        return form_action, form_data

    def res_servlet(self, url):
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Referer": "https://b-hpp.worldpay.com/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Priority": "u=0, i"
        }
        response = self.__http_utils.get(
            url=url,
            headers=headers, auth_redirect=True)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text
