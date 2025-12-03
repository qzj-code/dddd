"""
@Project     : flights
@Author      : ciwei
@Date        : 2024/3/18 19:29 
@Description : 
@versions    : 1.0.0.0
"""
import binascii
import hashlib
import io
import json
import math
import random
import time
from typing import List, Optional

import cv2
import httpx
import numpy as np
import rsa
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from PIL import Image

from common.utils.http_utils import CurlHttpUtil


class GeeTestUitls:

    def __init__(self, gt: str, challenge: str, proxy_info=None):

        self._http = CurlHttpUtil(proxy_info=proxy_info)
        self._http.initialize_http_util()
        self._http.verify = False
        self._gt = gt
        self._challenge = challenge
        self._aes_key = None

    def auth_geetest(self):

        response, _aes_key = self.init_geetest_data()

        cap_data = response.text[22:-1]
        cap_json = json.loads(cap_data)

        self.init_geetest_type(
            encrypt_c=cap_json['data']['c'],
            encrypt_s=cap_json['data']['s'],
            aes_key=_aes_key
        )

        response = self.get_geetest_check_data('slide3')
        cap_json = json.loads(response.text[22:-1])
        bg_response = self.get_check_image(url=cap_json['bg'])
        slice_response = self.get_check_image(url=cap_json['slice'])

        bg_png = self.restore_image_from_bytes(bg_response.body)
        slice_png = slice_response.body
        xy = self.find_and_display_gap(bg_png, slice_png)
        self._challenge = cap_json["challenge"]
        data = self.build_init_geetest_type_slice_data(self._gt, self._challenge, cap_json["c"], cap_json["s"], xy[0])
        response = self.submit_click_check(
            click_data=data
        )

        response_json = json.loads(response.text[22:-1])
        return response_json

    def init_geetest_data(self):

        headers = {
            "Host": "api.geetest.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "\"Windows\"",
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "script",
            "Referer": "https://www.transavia.com/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        data = {"gt": self._gt, "challenge": self._challenge,
                "lang": "zh", "offline": False, "new_captcha": True, "width": "100%", "product": "popup",
                "protocol": "https://", "type": "fullpage",
                "static_servers": ["static.geetest.com/", "static.geevisit.com/"],
                "beeline": "/static/js/beeline.1.0.1.js", "voice": "/static/js/voice.1.2.4.js",
                "click": "/static/js/click.3.1.0.js", "fullpage": "/static/js/fullpage.9.1.9-cyhomb.js",
                "slide": "/static/js/slide.7.9.2.js", "geetest": "/static/js/geetest.6.0.9.js",
                "aspect_radio": {"slide": 103, "click": 128, "voice": 128, "beeline": 50}, "cc": 16, "ww": True,
                "i": "-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1"}

        data, aes_key = self.encrypt_data_w(data, "pt")

        response = self._http.get(
            url=f"https://api.geetest.com/get.php?{data}",
            headers=headers
        )

        return response, aes_key

    def init_geetest_type(self, encrypt_c, encrypt_s, aes_key):

        headers = {
            "Host": "api.geevisit.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "\"Windows\"",
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "script",
            "Referer": "https://www.transavia.com/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        data = self.build_init_geetest_type_data(
            gt=self._gt,
            challenge=self._challenge,
            encrypt_c=encrypt_c,
            encrypt_s=encrypt_s
        )

        data, aes_key = self.encrypt_data_w(data, "pt", last_aes_key=aes_key)

        response = self._http.get(
            url=f"https://api.geevisit.com/ajax.php?{data}",
            headers=headers,

        )

    def get_geetest_check_data(self, check_type: str):
        headers = {
            "Host": "api.geevisit.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "\"Windows\"",
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "script",
            "Referer": "Referer: https://sso.ceair.com/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        url = f"https://api.geevisit.com/get.php?is_next=true&type={check_type}&gt={self._gt}&challenge={self._challenge}&lang=zh&https=false&protocol=https%3A%2F%2F&offline=false&product=popup&api_server=api.geevisit.com&isPC=true&autoReset=true&width=100%25&callback=geetest_1737024223678"
        response = self._http.get(
            url=url,
            headers=headers
        )
        return response

    def get_check_image(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        }

        response = self._http.get(
            url="https://static.geetest.com/" + url,
            headers=headers
        )
        return response

    def submit_click_check(self, click_data):

        headers = {
            "Host": "api.geevisit.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "\"Windows\"",
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "script",
            "Referer": "https://sso.ceair.com/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        # click_data = self.build_click_geetest_type_data(
        #     gt=self._gt,
        #     challenge=self._challenge,
        #     encrypt_c=encrypt_c,
        #     encrypt_s=encrypt_s,
        #     pic=pic,
        #     target_list=target_list
        # )

        data, aes_key = self.encrypt_data_w(click_data, "%24_BCN")
        response = self._http.get(
            url=f"https://api.geevisit.com/ajax.php?{data}",
            headers=headers,

        )

        return response

    def encrypt_data_w(self, data: any, submit_type: str, last_aes_key: Optional[str] = None):

        if last_aes_key is None:
            aes_key = self.build_aes_key()
        else:
            aes_key = last_aes_key

        _t = GeeTestUitls.aes_encrypt_hex(
            message_string=data if not isinstance(data, dict) else json.dumps(data).replace(' ', ''),
            key=aes_key
        )

        _t = list(bytes.fromhex(_t))
        _b = GeeTestUitls.bytes_data_encrypt(_t)

        _aes_key_rsa_encrypt = self.rsa_encrypt_string(aes_key)
        data = {
            "gt": self._gt,
            "challenge": self._challenge,
            "lang": "zh",
            submit_type: 0,
            "client_type": "web",
            "w": _b + _aes_key_rsa_encrypt if last_aes_key is None else _b
        }

        return "&".join([f"{key}={value}" for key, value in data.items()]) + "&callback=geetest_" + str(
            int(time.time()) * 1000), aes_key

    @classmethod
    def find_and_display_gap(cls, full_image_bytes, gap_template_bytes):
        """
        使用模板匹配识别滑块和缺口的位置。

        参数:
            full_image_bytes (bytes): 完整图片的二进制数据
            gap_template_bytes (bytes): 缺口图案的二进制数据

        返回:
            slider_center (tuple): 滑块中心坐标
            gap_center (tuple): 缺口中心坐标
            distance_x (int): 滑块和缺口在X轴上的距离
        """
        # 将字节数据解码为图像
        full_image_array = np.frombuffer(full_image_bytes, np.uint8)
        gap_template_array = np.frombuffer(gap_template_bytes, np.uint8)
        full_image = cv2.imdecode(full_image_array, cv2.IMREAD_COLOR)
        gap_template = cv2.imdecode(gap_template_array, cv2.IMREAD_COLOR)

        # 确保图片加载成功
        if full_image is None or gap_template is None:
            raise ValueError("无法加载图片，请检查输入数据是否正确")

        gap_template = gap_template[6:-6, 6:-6]

        # 将图像和模板转换为灰度图像
        full_image_gray = cv2.cvtColor(full_image, cv2.COLOR_BGR2GRAY)
        gap_template_gray = cv2.cvtColor(gap_template, cv2.COLOR_BGR2GRAY)

        # 使用模板匹配进行查找
        result = cv2.matchTemplate(full_image_gray, gap_template_gray, cv2.TM_SQDIFF_NORMED)

        # 获取匹配结果中最好的位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 设置匹配的阈值，低于该阈值的匹配认为是不合格的
        threshold = 0.5
        # if max_val < threshold:
        #     raise ValueError("匹配结果的相似度低于阈值，无法找到缺口图案")

        return max_loc

    @classmethod
    def restore_image_from_bytes(cls, image_bytes, ut=None):
        """
        根据乱码原图的字节数据和 Ut 数组还原图像。

        :param image_bytes: 乱码图像的字节数据
        :param ut: 乱序排列的小块图像索引数组 (默认为指定值)
        :return: 还原后的图像（PIL.Image 对象）
        """
        # 默认 Ut 数组
        if ut is None:
            ut = [
                39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51,
                33, 32, 28, 29, 27, 26, 36, 37, 31, 30, 44, 45,
                43, 42, 12, 13, 23, 22, 14, 15, 21, 20, 8, 9,
                25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18,
                16, 17
            ]

        # 加载乱码图像
        img = Image.open(io.BytesIO(image_bytes))

        # # 确保图像大小为 260x160
        # img = img.resize((312, 160))

        # 图像高度和块大小
        block_width = 10
        block_height = 80  # 160 / 2
        total_width = 260
        total_height = 160

        # 创建空白目标图像
        restored_img = Image.new("RGB", (total_width, total_height))

        # 遍历并还原图像块
        for idx in range(52):
            # 计算源块的位置
            c = ut[idx] % 26 * 12 + 1  # 起始 x 坐标
            u = block_height if ut[idx] > 25 else 0  # 起始 y 坐标

            # 裁剪出块区域
            block = img.crop((c, u, c + block_width, u + block_height))

            # 计算目标块的位置
            x_offset = (idx % 26) * block_width
            y_offset = block_height if idx > 25 else 0

            # 粘贴块到目标图像
            restored_img.paste(block, (x_offset, y_offset))

        buffer = io.BytesIO()
        restored_img.save(buffer, format="PNG")
        return buffer.getvalue()

    @classmethod
    def encode_direction(cls, t):
        """
        根据输入的方向 `t` 返回对应的字符编码。

        参数:
            t (list): 包含两个元素的列表，表示方向 [x, y]。

        返回:
            str: 对应的方向编码字符。
            int: 如果没有匹配的方向，返回 0。
        """
        # 定义方向列表和对应的编码字符
        directions = [[1, 0], [2, 0], [1, -1], [1, 1], [0, 1], [0, -1], [3, 0], [2, -1], [2, 1]]
        codes = 'stuvwxyz~'

        # 遍历方向列表，找到匹配的方向
        for n, direction in enumerate(directions):
            if t[0] == direction[0] and t[1] == direction[1]:
                return codes[n]

        # 如果未找到匹配方向，返回 0
        return 0

    @classmethod
    def generate_trajectory(cls, x_target):
        """
        根据目标 x 生成类似的轨迹数据。

        参数:
            x_target (int): 目标的 x 坐标值。

        返回:
            list: 轨迹数据列表，每个元素为 [x, y, t]。
        """
        trajectory = [
            [random.randint(-35, -30), random.randint(-25, -20), 0],
            [0, 0, 0],
        ]
        current_x, current_y, current_t = 0, 0, 0
        end = False
        end_distance = random.randint(-30, -20)
        # 逐步增加和减少步幅
        while current_x != x_target or not end:
            # 计算到目标的剩余距离
            remaining_distance = x_target - current_x

            # 判断是否已经超过目标距离
            if remaining_distance == end_distance:
                end = True

            if remaining_distance > 10:
                speed = random.randint(0, 2)
            elif remaining_distance < 10:
                speed = random.randint(0, 1) if not end else random.randint(-1, 0)
            else:
                speed = random.randint(0, 1)

            if random.random() > 0.3:
                dy = 0
            else:
                dy = 1

            if speed == 0:
                dt = random.randint(5, 15)
            else:
                if not end:
                    if remaining_distance > 10:
                        dt = random.randint(1, 2)
                    elif remaining_distance > 5:
                        dt = random.randint(20, 50)
                    elif remaining_distance > 3:
                        dt = random.randint(30, 50)
                    else:
                        dt = random.randint(300, 400)
                else:
                    if remaining_distance < 10:
                        dt = random.randint(1, 2)
                    elif remaining_distance < 5:
                        dt = random.randint(5, 15)
                    elif remaining_distance < 3:
                        dt = random.randint(15, 20)
                    else:
                        dt = random.randint(300, 400)
                speed_l = False

            # 更新当前位置
            current_x += speed
            current_y += dy
            current_t += dt

            # 添加轨迹点
            trajectory.append([current_x, current_y, current_t])

        trajectory.append([current_x, current_y, current_t])
        return trajectory, current_t

    @classmethod
    def simplify_trajectory(cls, t):
        """
        简化轨迹数据，合并连续的时间间隔或相同位移数据。

        参数:
            t (list): 轨迹数据，每个元素为 [x, y, timestamp]

        返回:
            list: 简化后的轨迹数据，每个元素为 [dx, dy, dt]
        """
        simplified = []
        carry_time = 0  # 用于累积时间间隔

        for s in range(len(t) - 1):
            e = round(t[s + 1][0] - t[s][0])  # dx
            n = round(t[s + 1][1] - t[s][1])  # dy
            r = round(t[s + 1][2] - t[s][2])  # dt

            if e == 0 and n == 0 and r == 0:
                # 跳过无效位移
                continue

            if e == 0 and n == 0:
                # 仅时间变化，累积时间间隔
                carry_time += r
            else:
                # 位移变化时，将当前点加入结果
                simplified.append([e, n, r + carry_time])
                carry_time = 0

        # 如果有剩余的累积时间，加入最后一个点
        if carry_time != 0:
            simplified.append([e, n, carry_time])

        return simplified

    @classmethod
    def build_init_geetest_type_slice_data(cls, gt, challenge, encrypt_c, encrypt_s, x):
        x -= 3
        init_trajectory_data, time_sum = cls.generate_trajectory(x)
        init_trajectory_data = cls.simplify_trajectory(init_trajectory_data)
        _r = []
        _i = []
        _o = []

        for index, value in enumerate(init_trajectory_data):
            t = cls.encode_direction(value)
            if t:
                _i.append(t)
            else:
                _r.append(cls.encode_value(value[0]))
                _i.append(cls.encode_value(value[1]))
            _o.append(cls.encode_value(value[2]))

        ccc = ''.join(_r) + "!!" + ''.join(_i) + "!!" + ''.join(_o)
        # 当前时间
        current_time = int(time.time()) * 1000

        # 开始时间
        start_time = current_time - random.randint(60000, 65000)

        def generate_timestamps(initial_timestamp, count):
            timestamps = {}
            current_timestamp = initial_timestamp

            # Generate the sequence
            for i in range(count):
                key = chr(97 + i)  # Generate 'a' to 'u' keys
                timestamps[key] = current_timestamp

                # Increment the timestamp by a small random number (1-10 ms)
                current_timestamp += random.randint(1, 10)

            return timestamps

        generate_timestamps(start_time, 21)

        a_time = start_time
        b_time = a_time + random.randint(100, 130)
        c_time = b_time
        d_time = 0
        e_time = 0
        f_time = a_time + random.randint(3, 5)
        g_time = f_time
        h_time = f_time
        i_time = f_time
        j_time = f_time
        k_time = 0
        l_time = f_time + 1
        m_time = a_time + random.randint(80, 100)
        n_time = m_time
        o_time = n_time + random.randint(8, 10)
        p_time = o_time + random.randint(200, 300)
        q_time = p_time
        r_time = q_time
        s_time = r_time + random.randint(300, 500)
        t_time = s_time
        u_time = t_time

        pass_time = time_sum

        data = {
            "lang": "zh",
            "userresponse": cls.x_process_string(x, challenge),
            "passtime": pass_time,
            "imgload": random.randint(60, 100),
            "aa": cls.string_data_encrypt(
                message_string=ccc,
                t=encrypt_c,
                n=encrypt_s
            ),
            "ep": {
                "v": "7.9.2",
                "$_BIE": False,
                "me": True,
                "tm": {
                    "a": a_time,
                    "b": b_time,
                    "c": c_time,
                    "d": d_time,
                    "e": e_time,
                    "f": f_time,
                    "g": g_time,
                    "h": h_time,
                    "i": i_time,
                    "j": j_time,
                    "k": k_time,
                    "l": l_time,
                    "m": m_time,
                    "n": n_time,
                    "o": o_time,
                    "p": p_time,
                    "q": q_time,
                    "r": r_time,
                    "s": s_time,
                    "t": t_time,
                    "u": u_time
                },
                "td": -1
            },
            "h9s9": "1816378497",
            "rp": cls.md5_encrypt(f"{gt}{challenge[0:32]}{pass_time}".encode())
        }
        return json.dumps(data, separators=(",", ":"))

    @classmethod
    def build_init_geetest_type_data(cls, gt, challenge, encrypt_c, encrypt_s):

        # 开始点击验证
        # 初始化坐标轨迹
        init_trajectory_encrypt_data, trajectory_result_array, pass_time = GeeTestUitls.trajectory_generate(
            target_list=[
                (random.randint(500, 800), random.randint(100, 500)),
                (random.randint(800, 1000), random.randint(100, 500)),
                (random.randint(1000, 1200), random.randint(100, 500))
            ],
            confirm_button_x=random.randint(1100, 1300),
            confirm_button_y=random.randint(800, 850)
        )

        current_time = int(time.time()) * 1000
        start_time = current_time - random.randint(60000, 85000)

        a_time = start_time - random.randint(100, 200)
        f_time = a_time + random.randint(10, 20)
        l_time = f_time + 1
        m_time = l_time + random.randint(20, 30)
        o_time = m_time + random.randint(3, 5)
        p_time = o_time + random.randint(10, 20)
        s_time = p_time + random.randint(100, 200)

        # 未知空值
        _t = GeeTestUitls.trajectory_encipher([])  # 8081
        # 对明文字符串进行第一次加密
        _t_bytes_encrypt_string = GeeTestUitls.bytes_data_encrypt(list(_t.encode()))
        # 第二次md5加密
        _t_md5_string = cls.md5_encrypt(_t_bytes_encrypt_string.encode())

        # Dom组件数据
        _dom_data = "-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1magic data-1"
        _dom_data_bytes_encrypt_string = GeeTestUitls.bytes_data_encrypt(list(_dom_data.encode()))
        _dom_data_md5_string = cls.md5_encrypt(_dom_data_bytes_encrypt_string.encode())
        _dom_data_string_md5_string = cls.md5_encrypt(_dom_data.encode())

        _dom_data_2 = "-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1"
        _dom_data_2_md5_string = cls.md5_encrypt(_dom_data_2.encode())

        # Div数据
        _div_data = ''

        # 加密数据明文数组
        _data = [
            ["lang", "zh-cn"],
            ["type", "fullpage"],
            ["tt", cls.string_data_encrypt(
                message_string=init_trajectory_encrypt_data,
                t=encrypt_c,
                n=encrypt_s
            )],
            ["light", "DIV_0|INPUT_1|INPUT_2|SPAN_3|DIV_4"],
            ["s", _t_md5_string],
            ["h", _dom_data_md5_string],
            ["hh", _dom_data_string_md5_string],
            ["hi", _dom_data_2_md5_string],
            ["vip_order", -1],
            ["ct", -1],
            ["ep",
             {
                 "v": "9.1.9-cyhomb",
                 "te": False,
                 "$_BCr": True,
                 "ven": "Google Inc. (NVIDIA)",
                 "ren": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4080 SUPER (0x00002702) Direct3D11 vs_5_0 ps_5_0, D3D11)",
                 "fp": trajectory_result_array[0],
                 "lp": trajectory_result_array[-1],
                 "em": {
                     "ph": 0,
                     "cp": 0,
                     "ek": "11",
                     "wd": 1,
                     "nt": 0,
                     "si": 0,
                     "sc": 0
                 },
                 "tm": {
                     "a": start_time - random.randint(100, 200),
                     "b": 0,
                     "c": 0,
                     "d": 0,
                     "e": 0,
                     "f": f_time,
                     "g": f_time,
                     "h": f_time,
                     "i": f_time,
                     "j": f_time,
                     "k": 0,
                     "l": l_time,
                     "m": m_time,
                     "n": m_time,
                     "o": o_time,
                     "p": p_time,
                     "q": p_time,
                     "r": p_time,
                     "s": s_time,
                     "t": s_time,
                     "u": s_time
                 },
                 "dnf": "dnf",
                 "by": 0
             }
             ],
            ["passtime", pass_time],
            ["rp", cls.md5_encrypt(f"{gt}{challenge}{pass_time}".encode())],
            ["captcha_token", "1533537096"],
            ["ydue", "hfoj0glb"]
        ]

        result_text = ",".join(
            f'"{x[0]}":{cls.stringify(x[1])}' for x in _data)
        result_text = "{" + result_text + "}"
        return result_text

    @classmethod
    def stringify(cls, message_string: any):
        if isinstance(message_string, (int, float)):
            return message_string
        elif isinstance(message_string, str):
            return f'"{message_string}"'
        elif isinstance(message_string, dict):
            return json.dumps(message_string).replace(" ", "")
        else:
            return message_string

    @classmethod
    def md5_encrypt(cls, message_bytes: bytes):
        md5_hash = hashlib.md5()
        md5_hash.update(message_bytes)
        hex_md5 = md5_hash.hexdigest()
        return hex_md5

    @classmethod
    def _encrypt_d(cls, data):
        _h = {"move": 0, "down": 1, "up": 2, "scroll": 3, "focus": 4, "blur": 5, "unload": 6, "unknown": 7}
        _n = len(data)
        _r = 0
        _t = []
        while _r < _n:
            i = data[_r]
            s = 0
            while True:
                if s >= 16:
                    break
                o = _r + s + 1
                if o >= _n:
                    break
                if data[o] != i:
                    break
                s += 1
            _r = _r + 1 + s
            if i in _h:
                _ = _h[i]
            else:
                _ = 0  # 如果 h 中没有 i 的编码，使用 0 作为默认值
            if s != 0:
                _t.append(8 | _)
                _t.append(s - 1)
            else:
                _t.append(_)

        # 假设 p 是一个已经定义的函数，用于处理整数和返回一个字符串。
        # 由于原始代码中没有提供 p 的具体实现，这里需要根据实际情况定义。
        # 例如，p 可以简单地将整数转换为其二进制表示的字符串。
        def p(x, y):
            return format(x, 'b').zfill(y)

        a = p(32768 | _n, 16)
        c = ''  # 初始化 c 为一个空字符串
        for l in _t:
            c += p(l, 4)
        return a + c

    @classmethod
    def _p(cls, e, t):
        n = bin(e)[2:]
        # 初始化r为一个空字符串，这可能用于填充或其他目的
        r = ''
        # 在n的长度达到t时停止，每次循环增加一个字符，这里假设增加的是'0'
        for i in range(len(n) + 1, t + 1):
            r += '0'  # 假设增加的字符是'0'，根据实际情况调整
        # 返回最终的字符串，这里假设是将r添加到n的前面
        return r + n

    @classmethod
    def _encrypt_g(cls, data, is_t: bool):
        # 假设：此函数中使用的外部函数需要根据实际情况进行定义或替代。
        # 例如，Math.abs, Math.ceil 等 JS 函数在 Python 中分别对应 abs, math.ceil。

        def a(e):
            # 假定 c 是某种特定的处理函数，可能涉及到数据的预处理或验证。
            # 这里暂时将其视为直接返回输入值的函数。
            def c(e, func):
                return [func(item) for item in e]

            t = 32767
            e = c(e, lambda x: max(min(t, x), -t))
            n = len(e)
            r = 0
            i = []
            while r < n:
                s = 1
                o = e[r]
                _ = abs(o)
                while True:
                    if r + s >= n or e[r + s] != o or _ >= 127 or s >= 127:
                        break
                    s += 1
                if s > 1:
                    i.append((o < 0) * 49152 | 32768 | s << 7 | _)
                else:
                    i.append(o)
                r += s

            return i

        def f_e(e):
            t = math.ceil(math.log(abs(e) + 1, 16))
            t = max(t, 1)  # 确保 t 至少为 1

            # 向 r 和 i 添加元素。这里使用简化的假设实现。
            _s.append(cls._p(t - 1, 2))
            _o.append(cls._p(abs(e), 4 * t))

        _s, _o, _n = [], [], []
        _e = a(data)
        for i in _e:
            f_e(i)

        if is_t:
            __n = []
            for i in _e:
                if 0 != i and i >> 15 != 1:
                    __n.append(i)

            for i in __n:
                if i < 0:
                    _n.append("1")
                else:
                    _n.append("0")

        return cls._p(32768 | len(_e), 16) + "".join(_s) + "".join(_o) + "".join(_n)

    @classmethod
    def encode_value(cls, t):
        """
        根据给定的逻辑对输入值进行编码。

        参数:
            t (int): 输入的整数值

        返回:
            str: 编码后的字符串
        """
        e = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr"
        n = len(e)
        r = ""
        i = abs(t)
        o = i // n  # 计算商

        if n <= o:
            o = n - 1  # 防止超出范围

        if o:
            r = e[o]  # 获取编码字符

        s = ""
        if t < 0:
            s += "!"  # 表示负号
        if r:
            s += "$"  # 表示商的存在

        # 取模计算剩余部分并返回结果
        return s + r + e[i % n]

    @classmethod
    def trajectory_encipher(cls, trajectory_array):
        _t = []
        _r = []
        _i = []
        _n = []
        for index, value in enumerate(trajectory_array):
            if len(value) != 5:
                raise Exception("未知坐标类型")

            _n.append(value[3])
            _r.append(value[1] if index == 0 else value[1] - trajectory_array[index - 1][1])
            _i.append(value[2] if index == 0 else value[2] - trajectory_array[index - 1][2])
            _t.append(value[0])

        c = f"{cls._encrypt_d(_t)}{cls._encrypt_g(_n, False)}{cls._encrypt_g(_r, True)}{cls._encrypt_g(_i, True)}"
        l = len(c)
        if l % 6 != 0:
            c += cls._p(0, 6 - l % 6)

        # 初始化结果字符串
        t = ''
        # 计算分组数量，原代码似乎是直接取整，这里使用整数除法
        n = len(c) // 6
        for r in range(n):
            # 截取字符串的每6位，并将其从二进制转换为整数
            segment = c[6 * r: 6 * (r + 1)]
            index = int(segment, 2)  # 将二进制字符串转换为整数
            # 使用转换后的整数作为索引，从charset中获取相应的字符
            t += '()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~'[index]

        return t

    @classmethod
    def build_aes_key(cls):

        def a():
            random_int = random.randint(4096, 65535)
            # 将整数转换为十六进制字符串并去除"0x"前缀。
            hex_str = hex(random_int)[2:]
            return hex_str

        return a() + a() + a() + a()

    @classmethod
    def rsa_encrypt_string(cls, message_string: str):
        """
        rsa加密
        :param message_string:
        :return:
        """

        modulus_hex = "00C1E3934D1614465B33053E7F48EE4EC87B14B95EF88947713D25EECBFF7E74C7977D02DC1D9451F79DD5D1C10C29ACB6A9B4D6FB7D0A0279B6719E1772565F09AF627715919221AEF91899CAE08C0D686D748B20A3603BE2318CA6BC2B59706592A9219D0BF05C9F65023A21D2330807252AE0066D59CEEFA5F2748EA80BAB81"
        exponent_hex = "10001"

        pub_key = rsa.PublicKey(int(modulus_hex, 16), int(exponent_hex, 16))
        crypto = rsa.encrypt(message_string.encode('utf8'), pub_key)
        return binascii.b2a_hex(crypto).decode()

    @classmethod
    def aes_encrypt_hex(cls, message_string: str, key: str):
        t = message_string.encode()
        cipher1 = AES.new(key.encode(), AES.MODE_CBC, '0000000000000000'.encode())
        # 使用对象进行加密，加密的时候，需要使用pad对数据进行填充，因为加密的数据要求必须是能被128整除
        # pad参数内容，第一个是待填充的数据，第二个是填充成多大的数据，需要填充成128位即16bytes
        ct = cipher1.encrypt(pad(t, 16))
        return ct.hex()

    @classmethod
    def _GJI(cls, e):
        t = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()'
        return '.' if e < 0 or e >= len(t) else t[e]

    @classmethod
    def _HBT(cls, e, t):
        return e >> t & 1

    @classmethod
    def bytes_data_encrypt(cls, message_bytes):

        o = {
            '_GCK': 7274496,
            '_GDu': 9483264,
            '_GEk': 19220,
            '_GGr': 24,
            '_GBe': '.',
            '_GFY': 235  # 示例中没有提供'_GFY'的值，这里假设为0
        }

        def _t(e, t):
            n = 0
            for r in range(o['_GGr'] - 1, -1, -1):
                if cls._HBT(t, r) == 1:
                    n = (n << 1) + cls._HBT(e, r)
            return n

        n = ''
        r = ''
        s = len(message_bytes)
        for a in range(0, s, 3):
            if a + 2 < s:
                _ = (message_bytes[a] << 16) + (message_bytes[a + 1] << 8) + message_bytes[a + 2]
                n += cls._GJI(_t(_, o['_GCK'])) + cls._GJI(_t(_, o['_GDu'])) + cls._GJI(_t(_, o['_GEk'])) + cls._GJI(
                    _t(_, o['_GFY']))
            else:
                c = s % 3
                if c == 2:
                    _ = (message_bytes[a] << 16) + (message_bytes[a + 1] << 8)
                    n += cls._GJI(_t(_, o['_GCK'])) + cls._GJI(_t(_, o['_GDu'])) + cls._GJI(_t(_, o['_GEk']))
                    r = o['_GBe']
                elif c == 1:
                    _ = message_bytes[a] << 16
                    n += cls._GJI(_t(_, o['_GCK'])) + cls._GJI(_t(_, o['_GDu']))
                    r = o['_GBe'] + o['_GBe']

        return n + r

    @classmethod
    def string_data_encrypt(cls, message_string, t, n):
        if not t or not n:
            return message_string

        o = 0
        i = message_string
        s, a, _ = t[0], t[2], t[4]

        while o < len(n):
            r = n[o:o + 2]
            o += 2
            if not r:
                break

            c = int(r, 16)
            l = chr(c)
            u = (s * c * c + a * c + _) % len(message_string)
            i = i[:u] + l + i[u:]

        return i

    @classmethod
    def click_mark_encrypted(cls, data: float):
        return round(100 * data)

    @classmethod
    def x_process_string(cls, t, e):
        # 提取字符串的最后两个字符
        n = e[-2:]

        # 转换为数字
        r = []
        for i in range(len(n)):
            o = ord(n[i])  # 获取字符的 Unicode 值
            if o > 57:
                r.append(o - 87)  # 对字母字符进行转换
            else:
                r.append(o - 48)  # 对数字字符进行转换

        # 计算 n 的值
        n_value = 36 * r[0] + r[1]

        # 计算 a
        a = round(t) + n_value
        c = {}
        _ = [[], [], [], [], []]
        u = 0

        # 遍历 e 字符串中的每个字符
        for i in range(len(e)):
            s = e[i]
            if s not in c:
                c[s] = 1
                _[u].append(s)
                u = 0 if u == 4 else u + 1  # 控制 u 的循环

        # 处理 f 和 g
        f = a
        d = 4
        p = ""  # 初始化 p 为一个空字符串
        g = [1, 2, 5, 10, 50]

        while f > 0:
            if f >= g[d]:
                h = int(random.random() * len(_[d]))  # 生成一个随机索引
                p += _[d][h]  # 拼接结果字符串
                f -= g[d]
            else:
                _[d].pop()  # 删除最后一个元素
                g.pop()  # 删除 g 中的元素
                d -= 1  # 调整 d 的值

        return p

    @classmethod
    def process_events(cls, e, last_time=None, max_length=300):
        """
        处理事件数据，返回处理后的事件数组。

        :param e: 输入事件列表
        :param last_time: 上一次事件的时间戳
        :param max_length: 最大处理事件数量
        :return: 处理后的事件数组
        """
        t = 0  # 上一次事件的 x 坐标
        n = 0  # 上一次事件的 y 坐标
        r = []  # 处理后的事件列表

        if len(e) <= 0:
            return []

        # 定义事件分类
        movement_events = {"down", "move", "up", "scroll"}
        state_events = {"blur", "focus", "unload"}

        # 提取和限制输入事件的数量
        _ = e[-max_length:] if len(e) > max_length else e

        for u in _:
            p = u[0]  # 事件类型
            if p in movement_events:
                # 处理运动相关的事件
                if last_time is None:
                    last_time = u[3]

                r.append([
                    p,
                    [u[1] - t, u[2] - n],  # 相对于上一次的 x 和 y 偏移
                    (u[3] - last_time) if last_time is not None else None  # 相对于上一次的时间偏移
                ])

                # 更新状态
                t = u[1]
                n = u[2]
                last_time = u[3]

            elif p in state_events:
                # 处理状态相关的事件
                if last_time is None:
                    last_time = u[1]

                r.append([
                    p,
                    (u[1] - last_time) if last_time is not None else None  # 相对于上一次的时间偏移
                ])

                # 更新状态
                last_time = u[1]

        return r

    @classmethod
    def encode_events(cls, e):
        def pad_binary(value, length):
            """将整数转换为指定长度的二进制字符串，并在前面补零"""
            binary = bin(value)[2:]
            return binary.zfill(length)

        def compress_event_types(events, event_map):
            """压缩事件类型"""
            compressed = []
            n = len(events)
            r = 0

            while r < n:
                current = events[r]
                count = 0

                while count < 16:
                    next_index = r + count + 1
                    if next_index >= n or events[next_index] != current:
                        break
                    count += 1

                r += 1 + count
                event_code = event_map[current]
                if count > 0:
                    compressed.append(8 | event_code)
                    compressed.append(count - 1)
                else:
                    compressed.append(event_code)

            header = pad_binary(32768 | n, 16)
            body = ''.join(pad_binary(value, 4) for value in compressed)
            return header + body

        def clamp_values(values, limit):
            """限制值的范围"""
            return [min(limit, max(-limit, value)) for value in values]

        def compress_coordinates(values, include_sign_bit):
            """压缩坐标值"""
            clamped = clamp_values(values, 32767)
            compressed = []
            r = 0
            n = len(clamped)

            while r < n:
                count = 1
                current = clamped[r]
                abs_value = abs(current)

                while count < 128:
                    next_index = r + count
                    if next_index >= n or clamped[next_index] != current:
                        break
                    if abs_value >= 127 or count >= 127:
                        break
                    count += 1

                if count > 1:
                    flag = 49152 if current < 0 else 32768
                    compressed.append(flag | (count << 7) | abs_value)
                else:
                    compressed.append(current)

                r += count

            sizes = []
            values = []
            for value in compressed:
                size = 1 if value == 0 else (value.bit_length() + 3) // 4
                sizes.append(pad_binary(size - 1, 2))
                values.append(pad_binary(abs(value), size * 4))

            header = pad_binary(32768 | len(clamped), 16)
            body = ''.join(sizes) + ''.join(values)

            if include_sign_bit:
                signs = ''.join('1' if value < 0 else '0' for value in compressed if value != 0 and value >> 15 != 1)
                body += signs

            return header + body

        event_map = {
            "move": 0,
            "down": 1,
            "up": 2,
            "scroll": 3,
            "focus": 4,
            "blur": 5,
            "unload": 6,
            "unknown": 7
        }

        types, primary_values, x_coords, y_coords = [], [], [], []
        for event in e:
            types.append(event[0])
            if len(event) == 2:
                primary_values.append(event[1])
            else:
                primary_values.append(event[2] if len(event) > 2 else 0)
                x_coords.append(event[1] if len(event) > 3 else 0)
                y_coords.append(event[2] if len(event) > 4 else 0)

        compressed = (
                compress_event_types(types, event_map) +
                compress_coordinates(primary_values, include_sign_bit=False) +
                compress_coordinates(x_coords, include_sign_bit=True) +
                compress_coordinates(y_coords, include_sign_bit=True)
        )

        if len(compressed) % 6 != 0:
            compressed += pad_binary(0, 6 - len(compressed) % 6)

        char_set = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~"
        encoded = ''.join(
            char_set[int(compressed[i:i + 6], 2)]
            for i in range(0, len(compressed), 6)
        )
        return encoded

    @classmethod
    def trajectory_generate(cls,
                            target_list: List[tuple],
                            confirm_button_x: int,
                            confirm_button_y: int):
        """
        点击轨迹生成
        :param target_list:
        :param confirm_button_x:
        :param confirm_button_y:
        :return:
        """

        # 假设屏幕宽高为 1291 * 952
        # 且目标起始位置为470，310 目标大小为330 * 330 目标有效X,Y 至 800，640
        # 确认按钮起始坐标为684，650 有效大小为120 * 40 目标有效X,Y 至 800, 690
        # 给定初始坐标
        current_x, current_y = random.randint(1000, 1400), random.randint(100, 500)
        current_time = int(time.time() * 1000)
        # 结果坐标储存
        trajectory_result_array = [
            ["focus", current_time]
        ]

        target_list.append((confirm_button_x, confirm_button_y, True))

        temp_current = [current_x, current_y]
        current_int_time = 0
        for i in target_list:
            end_move = False
            while not end_move:

                for index, value in enumerate(temp_current):
                    if temp_current[index] != i[index]:
                        if temp_current[index] > i[index]:
                            temp_current[index] += random.choice([-1, 0])
                        else:
                            temp_current[index] += random.choice([0, 1, 2])

                if temp_current[0] == i[0] and temp_current[1] == i[1]:
                    current_time += random.randint(300, 500)
                    trajectory_result_array.append(
                        ["down", temp_current[0], temp_current[1], current_time, "pointermove"])
                    current_time += random.randint(10, 50)
                    trajectory_result_array.append(
                        ["up", temp_current[0], temp_current[1], current_time, "pointermove"])
                    end_move = True
                else:
                    if temp_current[0] - i[0] < 5 or temp_current[1] - i[1] < 5:
                        ttt = random.randint(5, 10)
                        current_time += ttt
                    else:
                        ttt = random.randint(1, 3)
                        current_time += ttt

                    current_int_time += ttt
                    trajectory_result_array.append(
                        ["move", temp_current[0], temp_current[1], current_time, "pointermove"])

        trajectory_encode_array = cls.process_events(trajectory_result_array)
        encode_trajectory = cls.encode_events(trajectory_encode_array)
        return encode_trajectory, trajectory_result_array, current_int_time

    @classmethod
    def captcha_post(cls, image_base64, image_base642, number, free=False, question_rect=None):
        payload = {'img': image_base64, 'img2': image_base642}
        if question_rect:
            payload['question_rect'] = question_rect

        response = httpx.post(
            f'http://www.ocr.mobi:20000/predict?key_code=ENSFKVmD&number={number}&free={free}',
            json=payload
        )

        response_json = json.loads(response.text)
        return response_json
