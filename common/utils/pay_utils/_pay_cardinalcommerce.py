"""
@Project     : zhongyi_flight
@Author      : ciwei
@Date        : 2024/6/30 20:32
@Description :
@versions    : 1.0.0.0
"""
import json
import urllib.parse
import uuid
from typing import Any, Optional

from bs4 import BeautifulSoup

from common.errors import HttpModuleError, HttpModuleErrorStateEnum, ServiceError, ServiceStateEnum
from common.models import ProxyInfoModel
from common.utils import StringUtil
from common.utils.http_utils import CurlHttpUtil


class PayCardinalcommerce:

    def __init__(self, proxy_info: Optional[ProxyInfoModel]):

        self.__http_utils = CurlHttpUtil()
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)

    def collect_post(self, data, mcs_id: bool = False):

        headers = {
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Origin": "https://pop.cellpointdigital.net",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "iframe",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9"
        }

        response = self.__http_utils.post(
            url="https://centinelapi.cardinalcommerce.com/V1/Cruise/Collect",
            headers=headers,
            data=data
        )

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        parameter_string_list = StringUtil.extract_all_between(response.text, '<input', '>')

        result_data = {}
        for i in parameter_string_list:
            name = StringUtil.extract_between(i, 'id=\'', '\'')
            value = StringUtil.extract_between(i, 'value="', '"')
            result_data[name] = value
        if mcs_id:
            soup = BeautifulSoup(response.text, "html.parser")
            mcs_input = soup.find("input", {"id": "mcsId"})
            return result_data, mcs_input.get("value") if mcs_input else None
        return result_data

    def rander_post(self, url: str, data: str):
        """
        函数名 rander_post ，对应的请求实际是 Render 打错字了，打成了rander
        Args:
            url:
            data:

        Returns:

        """
        headers = {
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Origin": "https://centinelapi.cardinalcommerce.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "iframe",
            "Referer": "https://centinelapi.cardinalcommerce.com/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9"
        }

        response = self.__http_utils.post(
            url=url,
            headers=headers,
            data=data, timeout=60
        )

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        result_text = StringUtil.extract_between(response.text, 'profiler.start(', ')')
        return json.loads(result_text)

    def notification_post(self, url: str, data: str):

        headers = {
            "Host": "geo.cardinalcommerce.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Origin": "https://triplink-acs-3ds-sgp.triplinkintl.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "iframe",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9"
        }

        response = self.__http_utils.post(
            url=url,
            headers=headers,
            data=data, timeout=60
        )

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

    def collect_redirect(self, data: str):

        headers = {
            "Host": "centinelapi.cardinalcommerce.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua-platform": "\"Windows\"",
            "Origin": "https://centinelapi.cardinalcommerce.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "iframe",
            "Referer": "https://centinelapi.cardinalcommerce.com/V1/Cruise/Collect",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9"
        }

        response = self.__http_utils.post(
            url='https://centinelapi.cardinalcommerce.com/V1/Cruise/CollectRedirect',
            headers=headers,
            data=data, timeout=60
        )

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

    def cardinalcommerce_init_jwt(self, jwt, user_agent, headers_options: dict = None):

        if headers_options is None:
            headers_options = {}

        headers = {
            "Host": "centinelapi.cardinalcommerce.com",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,ru;q=0.8,la;q=0.7,en;q=0.6,ku;q=0.5,be;q=0.4"
        }

        for key, value in headers_options.items():
            headers[key] = value

        submit_data = {
            "BrowserPayload": {
                "Order": {
                    "OrderDetails": {},
                    "Consumer": {
                        "BillingAddress": {},
                        "ShippingAddress": {},
                        "Account": {}
                    },
                    "Cart": [],
                    "Token": {},
                    "Authorization": {},
                    "Options": {},
                    "CCAExtension": {}
                },
                "SupportsAlternativePayments": {
                    "cca": True,
                    "hostedFields": False,
                    "applepay": False,
                    "discoverwallet": False,
                    "wallet": False,
                    "paypal": False,
                    "visacheckout": False
                }
            },
            "Client": {
                "Agent": "SongbirdJS",
                "Version": "1.35.0"
            },
            "ConsumerSessionId": None,
            "ServerJWT": jwt
        }

        response = self.__http_utils.post(
            url="https://centinelapi.cardinalcommerce.com/V1/Order/JWT/Init",
            data=submit_data,
            headers=headers
        )
        if response.status not in [200, 0]:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        return response.json

    def cardinalcommerce_render_get(self, url: str, user_agent: str, headers_options: dict = None):
        """

        Args:
            url:
            user_agent:
            headers_options:

        Returns:

        """
        if headers_options is None:
            headers_options = {}

        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://centinelapi.cardinalcommerce.com/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "iframe",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site"
        }

        for key, value in headers_options.items():
            headers[key] = value

        response = self.__http_utils.get(url=url, headers=headers)
        if response.status not in [200, 0]:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        render_data_text = StringUtil.extract_between(response.text, "profiler.start(", ");")
        render_data_json = json.loads(render_data_text)
        return render_data_json

    def cardinalcommerce_render_post(self, url: str, user_agent: str, data: Any, headers_options: dict = None):
        """

        Args:
            url:
            user_agent:
            headers_options:

        Returns:

        """
        if headers_options is None:
            headers_options = {}

        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://centinelapi.cardinalcommerce.com/",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "iframe",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site"
        }

        for key, value in headers_options.items():
            headers[key] = value

        response = self.__http_utils.post(url=url, headers=headers, data=data)
        if response.status not in [200, 0]:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        render_data_text = StringUtil.extract_between(response.text, "profiler.start(", ");")
        render_data_json = json.loads(render_data_text)
        return render_data_json

    def cardinalcommerce_save_browser_data(self,
                                           nonce: str,
                                           reference_id: str,
                                           org_unit_id: str,
                                           user_agent: str,
                                           referrer: str,
                                           headers_options: dict = None,
                                           origin: str = "CruiseAPI"):

        if headers_options is None:
            headers_options = {}

        headers = {
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://geo.cardinalcommerce.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

        for key, value in headers_options.items():
            headers[key] = value

        submit_data = {
            "Cookies": {
                "Legacy": True,
                "LocalStorage": True,
                "SessionStorage": True
            },
            "DeviceChannel": "Browser",
            "Extended": {
                "Browser": {
                    "Adblock": True, "AvailableJsFonts": [], "DoNotTrack": "unknown", "JavaEnabled": False},
                "Device": {"ColorDepth": 24, "Cpu": "unknown", "Platform": "Win32",
                           "TouchSupport": {"MaxTouchPoints": 0, "OnTouchStartAvailable": False,
                                            "TouchEventCreationSuccessful": False}}},
            "Fingerprint": str(uuid.uuid4().hex), "FingerprintingTime": 15,
            "FingerprintDetails": {"Version": "1.5.1"}, "Language": "zh-CN", "Latitude": None,
            "Longitude": None, "OrgUnitId": org_unit_id, "Origin": origin,
            "Plugins": ["PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf~pdf",
                        "Chrome PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf~pdf",
                        "Chromium PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf~pdf",
                        "Microsoft Edge PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf~pdf",
                        "WebKit built-in PDF::Portable Document Format::application/pdf~pdf,text/pdf~pdf"],
            "ReferenceId": reference_id,
            "Referrer": referrer,
            "Screen": {
                "FakedResolution": False,
                "Ratio": 1.7777777777777777,
                "Resolution": "2560x1440",
                "UsableResolution": "2560x1400",
                "CCAScreenSize": "01"  # "02"
            }, "CallSignEnabled": None,
            "ThreatMetrixEnabled": False, "ThreatMetrixEventType": "PAYMENT",
            "ThreatMetrixAlias": "Default", "TimeOffset": -480,
            "UserAgent": user_agent,
            "UserAgentDetails": {"FakedOS": False, "FakedBrowser": False},
            "BinSessionId": nonce}

        response = self.__http_utils.post(
            url="https://geo.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/SaveBrowserData",
            data=json.dumps(submit_data),
            headers=headers
        )
        if response.status not in [200, 0]:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

    def cs3ds2response(self, url, data, referer, ua):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://3dspay.jetblue.com',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': referer,
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': ua,
        }
        response = self.__http_utils.post(url=url, headers=headers, data=data)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def agent_views_web(self, pay_dict):
        headers = {
            'Host': 'cebupacificairpartners.payment.cellpointdigital.net',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'upgrade-insecure-requests': '1',
            'origin': 'https://partners-beta.cebupacificair.com',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'referer': 'https://partners-beta.cebupacificair.com/',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        url = 'https://cebupacificairpartners.payment.cellpointdigital.net/views/web.php'
        response = self.__http_utils.post(url=url, headers=headers, data=pay_dict)
        # self.rf_logger.info(response.text)
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        return response.text

    def agent_parse_web(self, html=''):
        import re
        web_dict = {}
        results_list = re.findall(r"setItem\('(.*?)', '(.*?)'\)", html)
        for key, val in results_list:
            web_dict[key] = val

        return web_dict

    def cruise_collect(self, data):
        # data = {
        #     'BIN': bin,
        #     'JWT': jwt,
        # }
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'null',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }

        response = self.__http_utils.post(
            url="https://centinelapi.cardinalcommerce.com/V2/Cruise/Collect",
            headers=headers,
            data=data
        )

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        if response.text.find('Cruise API - Collect') == -1:
            raise ServiceError(ServiceStateEnum.INVALID_DATA, 'paymentCollectResponseData')

        soup = BeautifulSoup(response.text, 'html.parser')
        div_inputs = {}
        for input_tag in soup.select("div.hide.outOfview > input"):
            input_id = input_tag.get("id")
            input_value = input_tag.get("value")
            if input_id:
                div_inputs[input_id] = input_value

        # 提取 <form> 中的 <input>
        form_inputs = {}
        form = soup.find("form", id="redirectionForm")
        if form:
            for input_tag in form.find_all("input"):
                input_id = input_tag.get("id")
                input_value = input_tag.get("value")
                if input_id:
                    form_inputs[input_id] = input_value

        form_action = form.get("action")
        form_method = form.get("method")

        return {
            'inputs': div_inputs,
            'formData': {
                'inputs': form_inputs,
                'action': form_action,
                'method': form_method
            }
        }

    def collect_redirect_v2(self, data):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://centinelapi.cardinalcommerce.com',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://centinelapi.cardinalcommerce.com/V2/Cruise/Collect',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }

        response = self.__http_utils.post(
            url='https://centinelapi.cardinalcommerce.com/V2/Cruise/CollectRedirect',
            headers=headers,
            data=data
        )

        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)

        if response.text.find('RedirectForm') != -1:
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find("form", id="RedirectForm")
            inputs = form.find_all("input")
            form_inputs = {input_tag.get("name"): input_tag.get("value") for input_tag in inputs}

            form_action = form.get("action")
            form_method = form.get("method")
            return {
                'inputs': form_inputs,
                'action': form_action,
                'method': form_method
            }

        return None

    def render_method_url(self, url: str, payload: str):
        """

        Args:
            url: https://geoissuer.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/RenderMethodURL
            payload:

        Returns:

        """
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://geo.cardinalcommerce.com",
            "upgrade-insecure-requests": "1",
            "sec-fetch-dest": "iframe",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "priority": "u=4",
            "te": "trailers"
        }
        response = self.__http_utils.post(
            url=url,
            headers=headers,
            data=urllib.parse.urlencode({
                'threeDSMethodData': payload
            }), auth_redirect=True
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
        soup = BeautifulSoup(response.text, "html.parser")
        hidden_inputs = {}
        for inp in soup.find_all("input", {"type": "hidden"}):
            name = inp.get("name") or inp.get("id")
            value = inp.get("value", "")
            if name:
                hidden_inputs[name] = value
        return hidden_inputs

    def cardinalcommerce_save_browser_data_v2(self, user_agent: str,
                                              org_unit_id: str,
                                              reference_id: str):
        headers = {
            'user-agent': user_agent,
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/json",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://geoissuer.cardinalcommerce.com",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "te": "trailers"
        }
        data = {
            "Cookies": {
                "Legacy": True,
                "LocalStorage": True,
                "SessionStorage": True
            },
            "DeviceChannel": "Browser",
            "Extended": {
                "Browser": {
                    "Adblock": True,
                    "AvailableJsFonts": [],
                    "DoNotTrack": "unspecified",
                    "JavaEnabled": False
                },
                "Device": {
                    "ColorDepth": 30,
                    "Cpu": "unknown",
                    "Platform": "MacIntel",
                    "TouchSupport": {
                        "MaxTouchPoints": 0,
                        "OnTouchStartAvailable": False,
                        "TouchEventCreationSuccessful": False
                    }
                }
            },
            "Fingerprint": str(uuid.uuid4().hex),
            "FingerprintingTime": 29,
            "FingerprintDetails": {
                "Version": "1.5.1"
            },
            "Language": "zh-CN",
            "Latitude": None,
            "Longitude": None,
            "OrgUnitId": org_unit_id,
            "Plugins": [
                "PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf~pdf",
                "Chrome PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf~pdf",
                "Chromium PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf~pdf",
                "Microsoft Edge PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf~pdf",
                "WebKit built-in PDF::Portable Document Format::application/pdf~pdf,text/pdf~pdf"
            ],
            "ReferenceId": reference_id,
            "Referrer": "",
            "Screen": {
                "FakedResolution": False,
                "Ratio": 1.5397775876817792,
                "Resolution": "1800x1169",
                "UsableResolution": "1800x1037",
                "CCAScreenSize": "01"
            },
            "CallSignEnabled": False,
            "ThreatMetrixEnabled": True,
            "ThreatMetrixEventType": "PAYMENT",
            "ThreeDSServerTransId": reference_id,
            "TimeOffset": -480,
            "UserAgent": user_agent,
            "UserAgentDetails": {
                "FakedOS": False,
                "FakedBrowser": False
            }
        }
        response = self.__http_utils.post(
            url="https://geoissuer.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/SaveBrowserData",
            headers=headers,
            data=json.dumps(data)
        )
        if response.status != 200:
            raise HttpModuleError(HttpModuleErrorStateEnum.HTTP_RESPONSE_STATE_CODE_NOT_MEET_EXPECTATIONS,
                                  response.status)
