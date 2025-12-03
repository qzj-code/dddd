"""
Module: 第三方接口封装 - YesCaptcha
Author: likanghui
Date: 2024-10-31

Description:
    本模块用于封装 YesCaptcha 平台的验证码求解服务，包括：
    - Cloudflare Turnstile
    - hCaptcha
    - Google reCAPTCHA
"""

import traceback
from time import sleep
from typing import Optional, Tuple, Any

import requests

from common.errors import APIError, ApiStateEnum
from common.models import ProxyInfoModel
from common.utils import LogUtil


class YesCaptcha:
    def __init__(self, client_key: str, proxy_info: Optional[ProxyInfoModel] = None, retries: int = 15, delay: int = 5):
        """
        初始化 YesCaptcha 客户端

        Args:
            client_key (str): YesCaptcha API 密钥
            proxy_info (Optional[ProxyInfoModel]): 可选代理信息
            retries (int): 任务查询最大重试次数
            delay (int): 重试间隔（秒）
        """
        self._log = LogUtil("YesCaptcha")
        self._client_key = client_key
        self._retries = retries
        self._delay = delay
        self._proxy = f'http://{proxy_info.get_proxy_info_string()}' if proxy_info else None

    def solve_cloudflare_cookies(self, url: str, user_agent: Optional[str], wait_load: bool = False) -> dict:
        """
        创建并获取 Cloudflare cf_clearance Cookie 任务

        Args:
            url (str): 目标网站地址
            user_agent (Optional[str]): 可选的 UA
            wait_load (bool): 是否等待页面完全加载

        Returns:
            dict: 包含 Cookie 等字段的任务结果
        """
        task_data = {
            "type": "CloudFlareTaskS2",
            "websiteURL": url,
            "proxy": self._proxy,
            "waitLoad": wait_load,
            "requiredCookies": ["cf_clearance"]
        }
        if user_agent:
            task_data["userAgent"] = user_agent

        task_id = self.create_task(task_data)
        self._log.info(f"[Cloudflare Cookie] task_id: {task_id}")
        return self.get_task_result(task_id, task_type="CloudFlare")

    def solve_cloudflare_token(self, website_url: str, website_key: str) -> dict:
        """
        获取 Cloudflare Turnstile Token（无代理）

        Args:
            website_url (str): 目标页面地址
            website_key (str): Turnstile 公钥

        Returns:
            dict: 包含 gRecaptchaResponse 的任务结果
        """
        task_data = {
            "type": "TurnstileTaskProxyless",
            "websiteURL": website_url,
            "websiteKey": website_key
        }
        task_id = self.create_task(task_data)
        self._log.info(f"[Cloudflare Token] task_id: {task_id}")
        return self.get_task_result(task_id, task_type="CloudFlareToken")

    def solve_hcaptcha(self, sitekey: str, url: str, user_agent: Optional[str] = None,
                       is_invisible: bool = False, rqdata: str = "") -> Tuple[Any, Any]:
        """
        获取 hCaptcha Token（支持代理）

        Args:
            sitekey (str): hCaptcha 公钥
            url (str): 页面地址
            user_agent (Optional[str]): 用户代理
            is_invisible (bool): 是否为隐形验证码
            rqdata (str): 可选 rqdata 参数

        Returns:
            Tuple[Any, Any]: (token, user_agent)
        """
        task_data = {
            "type": "HCaptchaTaskProxyless",
            "websiteKey": sitekey,
            "websiteURL": url,
            "proxy": self._proxy,
            "isInvisible": is_invisible,
            "rqdata": rqdata
        }
        if user_agent:
            task_data["userAgent"] = user_agent

        task_id = self.create_task(task_data)
        self._log.info(f"[hCaptcha] task_id: {task_id}")
        result = self.get_task_result(task_id, task_type="hCaptcha")
        return result["gRecaptchaResponse"], result["userAgent"]

    def solve_recaptcha(self, site_url: str, site_key: str, is_invisible: bool = False) -> str:
        """
        获取 Google reCAPTCHA Token（Proxyless）

        Args:
            site_url (str): 验证页面 URL
            site_key (str): reCAPTCHA site key
            is_invisible (bool): 是否为隐形 reCAPTCHA

        Returns:
            str: gRecaptchaResponse token
        """
        task_data = {
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": site_url,
            "websiteKey": site_key,
            "isInvisible": is_invisible
        }

        task_id = self.create_task(task_data)
        self._log.info(f"[reCAPTCHA] task_id: {task_id}")
        result = self.get_task_result(task_id, task_type="GoogleRecaptcha")
        return result['gRecaptchaResponse']

    def create_task(self, task_data: dict) -> str:
        """
        创建任务

        Args:
            task_data (dict): 任务数据

        Returns:
            str: 任务 ID

        Raises:
            APIError: 创建失败
        """
        data = {
            "clientKey": self._client_key,
            "task": task_data
        }
        self._log.info(f"创建任务数据: {data}")
        response = requests.post("https://api.yescaptcha.com/createTask", json=data, timeout=30, verify=False)
        if response.status_code != 200:
            raise APIError(ApiStateEnum.ERROR_INFO, f"创建任务失败 HTTP {response.status_code}")

        resp_json = response.json()
        if resp_json.get("errorId") != 0:
            raise APIError(ApiStateEnum.CLOUD_FLARE_SOLUTION_FAILURE, f"任务创建失败: {resp_json}")

        return resp_json["taskId"]

    def get_task_result(self, task_id: str, task_type: str) -> dict:
        """
        查询任务执行结果（带轮询）

        Args:
            task_id (str): 任务 ID
            task_type (str): 任务类型标识（用于日志）

        Returns:
            dict: 成功任务的 result 内容

        Raises:
            APIError: 查询失败或超时
        """
        payload = {
            "clientKey": self._client_key,
            "taskId": task_id
        }

        for i in range(self._retries):
            try:
                response = requests.post("https://api.yescaptcha.com/getTaskResult", json=payload, timeout=30)
                response.raise_for_status()
            except requests.exceptions.RequestException:
                self._log.error(f"[{task_type}] 获取任务结果异常: {traceback.format_exc()}")
                sleep(self._delay)
                continue

            result = response.json()
            self._log.info(f"[{task_type}] 第 {i + 1} 次查询结果: {result}")

            if result.get("errorId") == 1:
                raise APIError(ApiStateEnum.CLOUD_FLARE_SOLUTION_FAILURE, f"{task_type} 求解失败")

            if result.get("status") == "ready":
                return result.get("solution", {})

            sleep(self._delay)

        raise APIError(ApiStateEnum.ERROR_INFO, f"{task_type} 求解超时")
