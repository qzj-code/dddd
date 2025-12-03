import base64
import hashlib
import random
import re
import string
import time
from urllib import parse

from Crypto.Cipher import AES

from flights.airchina_ca.common.des_utils import Des3_utils


def make_io_ssystem_date():
    time_stamp = time.time()
    local_time = time.localtime(time_stamp)
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    ios = f"{str_time} - Asia/Shanghai GMT+08:00"
    return ios


def make_user_info3():
    t = str(int(time.time() * 1000))
    info3 = Des3_utils().str_enc(t, "DF", "48", "A5")
    return info3


def make_user_info4(req):
    req = re.sub("[\u4e00-\u9fa5]", "", req)
    if len(req) > 50:
        req = req[0:50]
    return hashlib.md5(req.encode(encoding='UTF-8')).hexdigest()


def get_user_info2(gt_token, main_app_version):
    a = f'{gt_token}A6A92{main_app_version}'
    return hashlib.md5(a.encode(encoding='UTF-8')).hexdigest()


def generate_canonical_string(params_dict):
    """
    完全复现Jadx中 m33486j 函数的逻辑。
    1. 按Key的字母顺序对参数进行排序。
    2. 对Value进行URL编码（空格转为'+'）。
    3. 将排序和编码后的键值对用'='和'&'拼接成规范化字符串。

    :param params_dict: 包含所有待签名参数的字典。
    :return: 用于签名的规范化字符串。
    """

    # 1. 按Key的字母顺序对参数进行排序
    # sorted(params_dict.items()) 默认就按key排序，返回一个元组列表
    sorted_items = sorted(params_dict.items())

    # 2. 准备一个列表来存放 "key=encoded_value" 的部分
    query_parts = []

    # 3. 遍历排序后的列表
    for key, value in sorted_items:
        # a. 将value转换为字符串，以防有数字等类型
        str_value = str(value)

        # b. 对value进行URL编码。Java的URLEncoder.encode(s, "UTF-8")
        #    会将空格编码为'+'，这与Python的urllib.parse.quote_plus行为一致。
        encoded_value = parse.quote_plus(str_value, encoding='utf-8')

        # c. 拼接 key=value 部分
        query_parts.append(f"{key}={encoded_value}")

    # 4. 用'&'将所有部分连接成最终的字符串
    canonical_string = "&".join(query_parts)

    return canonical_string


def ranstr(num):
    salt = ''.join(random.sample(string.ascii_letters + string.digits, num))
    return salt


def make_init_security_token0(device_id):
    a = device_id
    b = ranstr(8).upper()
    c = hashlib.md5(a.encode(encoding='UTF-8')).hexdigest().upper()
    b2 = c + 'eAX6hWgCfmN9KmgN4AFKLBabbfFC2BjC' + b
    b2 = hashlib.md5(b2.encode(encoding='UTF-8')).hexdigest().upper()
    b3 = b2 + b
    return b3


def make_dynamic_secret_key_token1(session_id, sign_token1):
    b = ranstr(8).lower()  # 8位小写
    b3 = hashlib.md5(session_id.encode(encoding='UTF-8')).hexdigest().upper()
    b4 = sign_token1 + b3 + b
    b5 = hashlib.md5(b4.encode(encoding='UTF-8')).hexdigest().upper()
    return b5 + b


def make_server_securityToken2(session_id, user_id, sign_token1, sign_token2):
    b = ranstr(16).lower()
    obj = session_id + user_id  # 暂时不知道userId是什么
    b2 = hashlib.md5(obj.encode(encoding='UTF-8')).hexdigest().upper()
    obj2 = sign_token1
    b3 = obj2 + b2 + b + sign_token2
    b4 = hashlib.md5(b3.encode(encoding='UTF-8')).hexdigest().upper()
    return b + b4


def dict_to_custom_querystring(data_dict: dict) -> str:
    """
    将字典按照其默认顺序转换为查询字符串，并进行自定义的字符替换。
    不使用 urllib.parse.urlencode。
    :param data_dict: 输入的字典。
    :return: 格式化后的查询字符串。
    """
    # 1. 使用列表推导式生成 "key=value" 格式的字符串列表
    #    这里直接遍历字典的 .items() 即可，它会按插入顺序返回键值对
    query_parts = [f"{key}={value}" for key, value in data_dict.items()]
    # 2. 使用 '&' 将列表中的所有部分连接成一个完整的字符串
    query_string = "&".join(query_parts)
    # 3. 进行你指定的、链式的字符替换
    #    注意替换顺序，先替换 '%20' 再替换 ' ' 是个好习惯，避免二次替换
    final_string = query_string.replace('%20', '+').replace(' ', '+').replace('/', '%2F').replace(':', '%3A')

    return final_string


def aes_encrypt(data, aes_key):
    password = aes_key.encode('utf8')
    bs = AES.block_size

    # 这个有缺陷的pad函数，正是模仿的关键
    pad = lambda s: s + (bs - len(s.encode('utf8')) % bs) * chr(bs - len(s.encode('utf8')) % bs)

    cipher = AES.new(password, AES.MODE_ECB)

    # 整个流程：先对字符串进行一个奇怪的填充，然后对结果进行编码
    padded_data = pad(data)
    encrypted_bytes = cipher.encrypt(padded_data.encode('utf8'))

    return base64.b64encode(encrypted_bytes).decode('utf8')


def aes_decrypt(decr_data, aes_key):
    password = aes_key.encode('utf8')
    cipher = AES.new(password, AES.MODE_ECB)
    decrpytBytes = base64.b64decode(decr_data)
    # 这里的 decode 和 手动去填充，恰好是你加密过程的逆过程
    meg = cipher.decrypt(decrpytBytes).decode('utf-8')
    # 手动去除填充的逻辑
    padding_len = ord(meg[-1])
    return meg[:-padding_len]
