from typing import Optional, Dict, Tuple

import requests

from common.decorators.retry_decorator import retry_decorator
from common.errors import APIError, ApiStateEnum
from common.models import ProxyInfoModel
from common.utils import LogUtil
from common.utils.http_utils import TlsClientHttpUtil


class NoCaptcha:
    def __init__(self, client_key: str, proxy_info: Optional[ProxyInfoModel] = None, timeout: int = 30):
        """
        初始化 NoCaptcha 实例。

        Args:
            client_key (str): 第三方平台授权密钥。
            proxy_info (Optional[ProxyInfoModel]): 代理信息（用于接入国外资源）。
            timeout (int): 请求超时时间，单位为秒。
        """
        self.__timeout = timeout
        self.__client_key = client_key
        self.__proxy_info = proxy_info
        self.__proxy = f"http://{proxy_info.get_proxy_info_string()}" if proxy_info else None
        self.__proxy_region = proxy_info.region if proxy_info else None
        self.log = LogUtil("NoCaptcha")

        self.__http_utils = TlsClientHttpUtil(proxy_info=proxy_info, auth_manage_cookie=False)
        self.__http_utils.initialize_http_util(proxy_info=proxy_info)

    @property
    def _headers(self) -> Dict[str, str]:
        """构建请求头信息。"""
        return {
            'User-Token': self.__client_key,
            'Content-Type': 'application/json',
        }

    def _post(self, url: str, data: Dict, error_enum: ApiStateEnum) -> Dict:
        """
        发起 POST 请求，并处理异常与日志。

        Args:
            url (str): 请求地址。
            data (Dict): 请求参数。
            error_enum (ApiStateEnum): 请求失败时抛出的异常类型。

        Returns:
            Dict: 成功响应的 JSON 数据。
        """
        self.log.info(f"请求第三方接口: {url} 参数: {data}")
        try:
            response = requests.post(url, json=data, headers=self._headers, timeout=self.__timeout, verify=False)
            response_json = response.json()
            self.log.info(f"接口响应: {response_json}")
            if response_json.get('status') != 1:
                if response_json.get('msg', '') == '暂无可用破解器或并发超出上限':
                    raise APIError(ApiStateEnum.ERROR_INFO, "第三方服务资源不足")
                raise APIError(error_enum)
            return response_json
        except Exception as e:
            self.log.error(f"接口请求异常: {e}")
            raise APIError(error_enum)

    @retry_decorator(retry_service_error_list=[(ApiStateEnum.ERROR_INFO, None)], retry_max_number=20)
    def solve_hcaptcha(self, sitekey: str, referer: Optional[str] = None, domain: str = 'hcaptcha.com',
                       invisible: bool = False, need_ekey: bool = False, rqdata: Optional[str] = None) -> Tuple[
        str, Optional[str]]:
        """
        解决 Hcaptcha 验证码。

        Args:
            sitekey (str): Hcaptcha 网站公钥。
            referer (Optional[str]): 请求来源页面。
            domain (str): Hcaptcha 域名，默认为 'hcaptcha.com'。
            invisible (bool): 是否为隐形验证码。
            need_ekey (bool): 是否需要返回 ekey。
            rqdata (Optional[str]): 特殊数据参数。

        Returns:
            Tuple[str, Optional[str]]: 验证 UUID 和可选的 user-agent。
        """
        data = {
            "sitekey": sitekey,
            "referer": f"http://{referer}" if referer else None,
            "rqdata": rqdata,
            "domain": domain,
            "proxy": self.__proxy,
            "region": self.__proxy_region,
            "invisible": invisible,
            "need_ekey": need_ekey,
        }
        resp = self._post("http://api.nocaptcha.io/api/wanda/hcaptcha/universal", data,
                          ApiStateEnum.HCAPTCHA_SOLUTION_FAILURE)
        return resp['data']['generated_pass_UUID'], resp['data'].get('user_agent')

    @retry_decorator(retry_service_error_list=[(ApiStateEnum.ERROR_INFO, None)], retry_max_number=20)
    def solve_hcaptcha_v2(self, sitekey: str, href: Optional[str] = None, country: str = 'cn',
                          referer: Optional[str] = None, branch: str = 'mac1') -> Tuple[str, Dict]:
        """
        解决新版 Hcaptcha 验证码。

        Args:
            sitekey (str): Hcaptcha 网站公钥。
            href (Optional[str]): 页面地址。
            country (str): 国家代码。
            referer (Optional[str]): 来源页。
            branch (str): 模拟客户端分支。

        Returns:
            Tuple[str, Dict]: 验证 UUID 和 extra 数据。
        """
        data = {
            "branch": branch,
            "href": href,
            "sitekey": sitekey,
        }
        if self.__proxy:
            resp = self.__http_utils.get(url="https://ipinfo.io/json", headers={
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            }, timeout=5).json
            data.update({
                "region": self.__proxy_region,
                "ip": resp.get("ip"),
                "timezone": resp.get("timezone"),
                "geolocation": resp.get("loc"),
                "proxy": self.__proxy
            })
        resp = self._post("http://api.nocaptcha.cn/api/wanda/hcaptcha/v2", data,
                          ApiStateEnum.HCAPTCHA_SOLUTION_FAILURE)
        return resp['data']['generated_pass_UUID'], resp['extra']

    def solve_akamai(self, href: str, api: str, is_auth: bool = True) -> Tuple[Dict, str, str]:
        """
        获取 Akamai 验证数据。

        Args:
            href (str): 当前页面地址。
            api (str): JavaScript 资源地址。
            is_auth (bool): 是否使用包月授权代理。

        Returns:
            Tuple[Dict, str, str]: 响应头信息、_abck 和 bm_sz。
        """
        data = {"href": href, "api": api, "is_auth": False}
        if is_auth:
            data["proxy"] = self.__proxy
        resp = self._post("http://api.nocaptcha.io/api/wanda/akamai/v2", data,
                          ApiStateEnum.AKM_SOLUTION_FAILURE)
        return resp["extra"], resp["data"]["_abck"], resp["data"]["bm_sz"]

    def solve_recaptcha(self, referer: str, sitekey: str, title: str,
                        size: str = "invisible", action: Optional[str] = None) -> str:
        """
        获取 Google reCAPTCHA Token。

        Args:
            referer (str): 来源页。
            sitekey (str): Google reCAPTCHA site key。
            title (str): 页面标题。
            size (str): 验证码尺寸（默认为 invisible）。
            action (Optional[str]): 执行动作名称。

        Returns:
            str: 验证 token。
        """
        data = {
            "referer": referer,
            "sitekey": sitekey,
            "size": size,
            "title": title,
            "action": action,
            "proxy": self.__proxy,
        }
        resp = self._post("http://api.nocaptcha.io/api/wanda/recaptcha/universal", data,
                          ApiStateEnum.RECAPTCHA_SOLUTION_FAILURE)
        return resp['data']['token']

    def solve_cf_turnstile(self, url: str, sitekey: str) -> Dict:
        """
        解决 Cloudflare Turnstile 验证。

        Args:
            url (str): 页面 URL。
            sitekey (str): Turnstile 验证公钥。

        Returns:
            Dict: 响应完整数据。
        """
        data = {
            "href": url,
            "sitekey": sitekey,
            "proxy": self.__proxy,
        }
        return self._post("http://api.nocaptcha.io/api/wanda/cloudflare/universal", data,
                          ApiStateEnum.CLOUD_FLARE_SOLUTION_FAILURE)

    def solve_cloudflare_cookies(self, url: str, user_agent: Optional[str]) -> dict:
        """
        创建并获取 Cloudflare cf_clearance Cookie 任务

        Args:
            url (str): 目标网站地址
            user_agent (Optional[str]): 可选的 UA

        Returns:
            dict: 包含 Cookie 等字段的任务结果
        """
        task_data = {
            "href": url,
            "proxy": self.__proxy,
        }
        if user_agent:
            task_data["user_agent"] = user_agent

        return self._post("http://api.nocaptcha.io/api/wanda/cloudflare/universal", task_data,
                          ApiStateEnum.CLOUD_FLARE_SOLUTION_FAILURE)
