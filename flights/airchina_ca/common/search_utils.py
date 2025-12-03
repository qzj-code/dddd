import base64
import hashlib
import random
import time
from math import isnan

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class AESCipher:
    def __init__(self, key: str):
        """
        初始化 AES 加密器。
        密钥（key）必须是 16 (AES-128), 24 (AES-192), or 32 (AES-256) 字节长。
        这里我们假设 key 是 UTF-8 编码的字符串。
        """
        # 将字符串密钥编码为字节
        self.key = key.encode('utf-8')
        # AES.block_size 恒为 16 (字节)
        self.block_size = AES.block_size

    def encrypt(self, data: str, iv: str) -> str:
        """
        加密数据，对应 CryptoJS 的 AES.encrypt。

        :param data: 待加密的明文字符串。
        :param iv: 初始向量 (Initialization Vector) 字符串，必须是16字节长。
        :return: Base64 编码的密文字符串。
        """
        # 将明文和 IV 编码为字节
        data_bytes = data.encode('utf-8')
        iv_bytes = iv.encode('utf-8')

        # 创建一个 AES 密码器，使用 CBC 模式和指定的 IV
        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv_bytes)

        # 对数据进行 PKCS7 填充，然后加密
        # pad() 函数的第二个参数是块大小，对于AES总是16
        padded_data = pad(data_bytes, self.block_size)
        encrypted_bytes = cipher.encrypt(padded_data)

        # 将加密后的字节数据进行 Base64 编码，并返回字符串
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    def decrypt(self, encrypted_data: str, iv: str) -> str:
        """
        解密数据。

        :param encrypted_data: Base64 编码的密文字符串。
        :param iv: 与加密时使用的相同的初始向量 (IV) 字符串。
        :return: 解密后的明文字符串。
        """
        # 将 Base64 编码的密文和 IV 解码/编码为字节
        encrypted_bytes = base64.b64decode(encrypted_data)
        iv_bytes = iv.encode('utf-8')

        # 创建一个 AES 密码器
        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv_bytes)

        # 解密数据
        decrypted_padded_bytes = cipher.decrypt(encrypted_bytes)

        # 去除 PKCS7 填充
        decrypted_bytes = unpad(decrypted_padded_bytes, self.block_size)

        # 将解密后的字节数据解码为字符串并返回
        return decrypted_bytes.decode('utf-8')


def get_feca(FECW, user_agent, start_time, server_time):
    ####
    # FECW
    # "None"
    # false 固定
    # "None" { "None": "00", "DebugJs": "01", "ConsoleCore": "02", "Other": "03"}
    # 001
    # 001 ###监控屏幕的点击次数
    # 000
    # fi   #采集的浏览器指纹的md5 ,直接随机
    # user_agent的md5
    # 浏览器种类 {"chrome": "1","firefox": "2","msie": "3","opera": "4","safari": "5","wechat": "6","qq": "7","uc": "8","other": "9"}
    # 自定义时间戳
    # Base64随机5位字符串

    def get_md5_hash(input_string: str) -> str:
        """
        计算输入字符串的MD5哈希值。

        :param input_string: 需要计算哈希的字符串。
        :return: 32个字符的小写十六进制MD5哈希值。
        """
        # 将字符串编码为utf-8字节序列，然后计算MD5哈希
        md5_hash = hashlib.md5(input_string.encode('utf-8')).hexdigest()
        return md5_hash

    def get_random_chars_choices(char_set: str, num_chars: int) -> str:
        """
        使用 random.choices 从字符串中随机选取指定数量的字符。
        允许字符重复。

        :param char_set: 包含所有可选字符的字符串。
        :param num_chars: 需要选取的字符数量。
        :return: 一个由随机字符组成的新字符串。
        """
        # random.choices 返回一个字符列表，例如 ['a', 'X', '7', 'k', 'b']
        random_chars_list = random.choices(char_set, k=num_chars)

        # 使用 ''.join() 将列表合并成一个字符串
        return "".join(random_chars_list)

    def generate_fake_md5() -> str:
        """
        通过从十六进制字符表中随机挑选32个字符，来构造一个看起来像MD5的字符串。

        这只是一个格式模拟，并非真实的哈希值。

        :return: 一个32位的小写十六进制“伪”MD5字符串。
        """
        # 1. 定义MD5哈希值中可能出现的所有字符（十六进制，小写）
        hex_chars = '0123456789abcdef'

        # 2. 从字符表中随机选择32次，组成一个列表
        #    random.choices 允许字符重复，这符合MD5的特性
        random_chars_list = random.choices(hex_chars, k=32)

        # 3. 将列表中的字符合并成一个字符串
        return "".join(random_chars_list)

    fi = generate_fake_md5()
    nowtime = int(time.time() * 1000) + random.randint(50, 255)
    enctimestamp = nowtime - start_time + int(server_time) * 0x3e8
    character_pool = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    random_string = get_random_chars_choices(character_pool, 5)

    enctext = f'{get_md5_hash(FECW)}{"00"}{"0"}{"00"}{"001"}{"001"}{"000"}{fi}{get_md5_hash(user_agent)}{"1"}{enctimestamp}{random_string}'
    my_key = "c77c9ccac77c9cca"  # 16字节 -> AES-128
    my_iv = "c77c9ccac77c9cca"  # 16字节
    cipher = AESCipher(key=my_key)

    aesenctext = cipher.encrypt(enctext, my_iv)
    return enctext[3] + aesenctext + enctext[7]


# --- 使用示例 ---
def get_server_time_from_string(long_string: str) -> dict:
    """
    将一个经过混淆的 JavaScript 函数转换为 Python。

    这个函数接收一个逗号分隔的长字符串，通过固定的索引规则
    重新组合字符，并从中提取 'key', 'server_time', 'is_debugger', 和 'secure' 等值。

    :param long_string: 从 JS 环境获取的逗号分隔的字符串。
    :return: 一个包含提取出信息的字典。
    """
    # 1. 准备阶段
    # JS: _0x5804cb = _0x225d15["split"](',')
    parts = long_string.split(',')

    # JS: _0x4142a6 = [0x2, 0x3, 0x6, 0x7, 0x8, 0x9]
    # 这些是用于选择 `parts` 列表中的哪个部分的索引（已减1）和计算字符位置的乘数。
    multipliers = [2, 3, 6, 7, 8, 9]

    # JS: _0x177a26 = '';
    # 这个变量将用来拼接所有挑选出来的字符。
    reconstructed_string = ''

    # 2. 核心的字符重组循环
    for multiplier in multipliers:
        # JS: for (var _0x82c385 = 0x1; _0x82c385 <= 0x20; _0x82c385++)
        # 0x20 等于 32。循环从 1 到 32。
        for counter in range(1, 33):  # range(1, 33) 产生 1, 2, ..., 32

            # JS: if ((_0x82c385 *  _0x19f8b4) >= 0x20 + _0x19f8b4) break;
            # 这是一个提前终止内层循环的条件
            if (counter * multiplier) >= (32 + multiplier):
                break

            # JS: _0x177a26 += _0x5804cb[_0x19f8b4 - 0x1][...];
            # a. 选择源字符串: JS中数组索引从0开始，所以 multiplier - 1
            source_string = parts[multiplier - 1]

            # b. 计算要抽取的字符的索引
            # JS: ((((_0x82c385 * _0x19f8b4 + 0x1)% 0x20) - 0x1))
            char_index = (((counter * multiplier + 1) % 32) - 1)

            # c. 从源字符串中抽取字符并拼接到结果中
            reconstructed_string += source_string[char_index]

    # 3. 切片并构造返回结果
    # JS: _0x177a26['slice'](0x0, 0x20)
    # 提取前 32 个字符作为 key
    key = reconstructed_string[0:32]

    # JS: _0x177a26['slice'](0x20, 0x2a)
    # 0x2a 等于 42。提取索引 32 到 41 的字符 (共10个) 作为 server_time
    server_time = reconstructed_string[32:42]

    # JS: _0x177a26[0x2a]
    # 提取索引为 42 的字符
    is_debugger = reconstructed_string[42]

    # JS: _0x177a26[0x2b]
    # 提取索引为 43 的字符
    secure = reconstructed_string[43]
    startime = int(time.time() * 1000)
    # 构造并返回一个字典，与JS对象的结构相同
    result = {
        'key': key,
        'start_time': startime,
        'server_time': server_time,
        'is_debugger': is_debugger,
        'secure': secure
    }

    return result


def generate_lid(length=32):
    """
    生成一个随机ID，格式为：当前时间戳 + 随机字符串
    参数:
        length (int): 随机字符串的长度，默认为32
    返回:
        str: 生成的ID
    """
    # 字符集（与JS完全一致）
    charset = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    # 生成随机字符部分
    random_part = ''.join([
        charset[random.randint(0, len(charset) - 1)]
        for _ in range(length)
    ])

    # 获取当前时间戳（毫秒级，与JS的getTime()一致）
    timestamp = int(time.time() * 1000)

    # 组合结果：时间戳 + 随机字符串
    return f"{timestamp}{random_part}"


def encod_constId(r, a):
    if not r:
        return ""

    p = ""
    C = 0
    length = len(r)

    while C < length:
        # 模拟 JS 的 charCodeAt，越界返回 NaN
        def charCodeAt(s, idx):
            return ord(s[idx]) if idx < len(s) else float('nan')

        i = charCodeAt(r, C)
        C += 1
        u = charCodeAt(r, C) if C < length else float('nan')
        C += 1
        s = charCodeAt(r, C) if C < length else float('nan')
        C += 1

        # 位运算逻辑（完全按照 JS 的方式处理 NaN）
        d = (int(i) >> 2) if not isnan(i) else 0
        h = ((3 & int(i)) << 4) | ((int(u) >> 4) if not isnan(u) else 0)

        if isnan(u):
            l = 64
            v = 64
        else:
            l = ((15 & int(u)) << 2) | ((int(s) >> 6) if not isnan(s) else 0)
            v = (63 & int(s)) if not isnan(s) else 64

        if isnan(s):
            v = 64

        # 拼接结果
        p += a[d] + a[h] + a[l] + a[v]

    return p


def simulate_device_memory(device_type="desktop"):
    def get_random_power_of_two(min_value, max_value):
        # 生成介于 min_value 和 max_value 之间的2的幂次值
        powers_of_two = []
        value = 1
        while value <= max_value:
            if value >= min_value:
                powers_of_two.append(value)
            value *= 2

        return random.choice(powers_of_two)

    if device_type == "desktop":
        # 模拟桌面设备的内存大小，通常在 4GB 到 32GB 之间
        memory = get_random_power_of_two(4, 128)
    elif device_type == "mobile":
        # 模拟移动设备的内存大小，通常在 1GB 到 8GB 之间
        memory = get_random_power_of_two(1, 8)
    else:
        # 默认情况：返回一个中等值
        memory = 4  # 4GB

    return memory


def generate_random_md5_like_string(length):
    if length <= 0:
        return ""

    # 生成一个随机字符串，只包含小写字母和数字
    characters = '0123456789abcdef'
    random_string = ''.join(random.choice(characters) for _ in range(length))

    # 返回生成的随机字符串
    return random_string


def simulate_webgl_info(platform='Win32'):
    # 模拟供应商和显卡型号
    is_mobile = False
    vendors = ["Google Inc.", "NVIDIA Corporation", "AMD", "Intel"]
    mobile_vendors = ["Qualcomm", "Apple", "ARM"]
    if platform != "Linux" and platform != 'Android' and platform != "":
        vendor = random.choice(vendors)
    else:
        is_mobile = True
        vendor = random.choice(mobile_vendors)

    if vendor == "NVIDIA Corporation":
        renderers = [
            "NVIDIA GeForce RTX 4090", "NVIDIA GeForce RTX 4080", "NVIDIA GeForce RTX 4070",
            "NVIDIA GeForce RTX 4060", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070",
            "NVIDIA GeForce RTX 3060", "NVIDIA GeForce GTX 1080 Ti", "NVIDIA GeForce GTX 1080",
            "NVIDIA GeForce GTX 1070", "NVIDIA GeForce GTX 1060", "NVIDIA GeForce GTX 1050 Ti",
            "NVIDIA GeForce GTX 1050", "NVIDIA GeForce GTX 1660", "NVIDIA GeForce GTX 1650",
            "NVIDIA GeForce GTX 970", "NVIDIA GeForce GTX 980", "NVIDIA GeForce GTX 980 Ti",
            "NVIDIA GeForce GT 1030", "NVIDIA GeForce GT 730", "NVIDIA Tesla P100",
            "NVIDIA Tesla K80", "NVIDIA Quadro P6000", "NVIDIA Quadro P4000",
            "NVIDIA Quadro M2000M", "NVIDIA Quadro K1200", "NVIDIA Quadro RTX 8000",
            "NVIDIA Quadro RTX 6000", "NVIDIA Quadro RTX 5000", "NVIDIA Quadro T2000"
        ]
    elif vendor == "AMD":
        renderers = [
            "AMD Radeon RX 6800 XT", "AMD Radeon RX 6900 XT", "AMD Radeon RX 5700 XT",
            "AMD Radeon RX 5700", "AMD Radeon RX 5600 XT", "AMD Radeon RX 5500 XT",
            "AMD Radeon Vega 64", "AMD Radeon Vega 56", "AMD Radeon RX 580",
            "AMD Radeon RX 590", "AMD Radeon RX 480", "AMD Radeon R9 Fury X",
            "AMD Radeon R9 390X", "AMD Radeon R9 290", "AMD Radeon RX 6800",
            "AMD Radeon RX 6700 XT", "AMD Radeon RX 6600 XT", "AMD Radeon Pro WX 7100",
            "AMD Radeon Pro WX 5100", "AMD Radeon Pro W5700", "AMD Radeon Pro 5700 XT",
            "AMD Radeon Pro 5600M", "AMD Radeon Pro 555X", "AMD Radeon Pro 5500M",
            "AMD Radeon Pro 5500 XT", "AMD FirePro W7100", "AMD FirePro W5000",
            "AMD FirePro W9100", "AMD FirePro W8000", "AMD Radeon RX 570"
        ]
    elif vendor == "Intel":
        renderers = [
            "Intel(R) UHD Graphics 620", "Intel(R) Iris Plus Graphics 640", "Intel(R) UHD Graphics 630",
            "Intel(R) Iris Xe MAX Graphics", "Intel(R) HD Graphics 630", "Intel(R) UHD Graphics",
            "Intel(R) HD Graphics 620", "Intel(R) HD Graphics 520", "Intel(R) Iris Plus Graphics",
            "Intel(R) Iris Graphics 6100", "Intel(R) HD Graphics 6000", "Intel(R) HD Graphics 5500",
            "Intel(R) HD Graphics 5300", "Intel(R) Iris Pro Graphics 580", "Intel(R) Iris Pro Graphics 6200",
            "Intel(R) Iris Pro Graphics 5200", "Intel(R) HD Graphics 4000", "Intel(R) HD Graphics 3000",
            "Intel(R) HD Graphics 2500", "Intel(R) HD Graphics 2000", "Intel(R) Iris Xe Graphics",
            "Intel(R) UHD Graphics P630", "Intel(R) HD Graphics P530", "Intel(R) HD Graphics P630",
            "Intel(R) HD Graphics P580", "Intel(R) Iris Plus Graphics 650", "Intel(R) Iris Plus Graphics G7",
            "Intel(R) Iris Plus Graphics G4", "Intel(R) HD Graphics 405", "Intel(R) UHD Graphics 605"
        ]
    elif vendor == "Qualcomm":
        renderers = [
            "Adreno (TM) 732", "Adreno (TM) 640", "Adreno (TM) 650", "Adreno (TM) 530",
            "Adreno (TM) 540", "Adreno (TM) 618", "Adreno (TM) 660", "Adreno (TM) 616",
            "Adreno (TM) 330", "Adreno (TM) 320", "Adreno (TM) 420", "Adreno (TM) 430",
            "Adreno (TM) 505", "Adreno (TM) 600", "Adreno (TM) 530", "Adreno (TM) 510",
            "Adreno (TM) 530", "Adreno (TM) 520", "Adreno (TM) 505", "Adreno (TM) 606",
            "Adreno (TM) 612", "Adreno (TM) 616", "Adreno (TM) 630", "Adreno (TM) 640",
            "Snapdragon 888", "Snapdragon 865", "Snapdragon 855", "Snapdragon 845",
            "Snapdragon 835", "Snapdragon 765", "Snapdragon 750G", "Snapdragon 730",
            "Snapdragon 712", "Snapdragon 710", "Snapdragon 675", "Snapdragon 660",
            "Snapdragon 650", "Snapdragon 630", "Snapdragon 625", "Snapdragon 617",
            "Snapdragon 618", "Snapdragon 616", "Snapdragon 810", "Snapdragon 800",
            "Snapdragon 660", "Snapdragon 430", "Snapdragon 400", "Snapdragon 212",
            "Snapdragon 200", "Snapdragon 801", "Snapdragon 615", "Snapdragon 412",
            "Qualcomm Snapdragon 888", "Qualcomm Snapdragon 865", "Qualcomm Snapdragon 855",
            "Qualcomm Snapdragon 845", "Qualcomm Snapdragon 835", "Qualcomm Snapdragon 765G",
            "Qualcomm Snapdragon 730G", "Qualcomm Snapdragon 720G", "Qualcomm Snapdragon 710",
            "Qualcomm Snapdragon 675", "Qualcomm Snapdragon 660", "Qualcomm Snapdragon 650",
            "Qualcomm Snapdragon 625", "Qualcomm Snapdragon 615", "Qualcomm Snapdragon 602A",
            "Qualcomm Snapdragon 410", "Qualcomm Snapdragon 425", "Qualcomm Snapdragon 430"
        ]

    elif vendor == "ARM":
        renderers = [
            "ARM Cortex-A78", "ARM Cortex-A77", "ARM Cortex-A76", "ARM Cortex-A75",
            "ARM Cortex-A73", "ARM Cortex-A72", "ARM Cortex-A71", "ARM Cortex-A70",
            "ARM Cortex-A55", "ARM Cortex-A53", "ARM Cortex-A52", "ARM Cortex-A50",
            "ARM Cortex-A9", "ARM Cortex-A8", "ARM Cortex-A7", "ARM Cortex-A15",
            "ARM Cortex-M7", "ARM Cortex-M4", "ARM Cortex-M3", "ARM Cortex-M0",
            "ARM Mali-G77", "ARM Mali-G76", "ARM Mali-G75", "ARM Mali-G72",
            "ARM Mali-G71", "ARM Mali-G68", "ARM Mali-G57", "ARM Mali-G52",
            "ARM Mali-G51", "ARM Mali-G31", "ARM Mali-T880", "ARM Mali-T860",
            "ARM Mali-T820", "ARM Mali-T700", "ARM Mali-T604", "ARM Mali-400 MP4",
            "ARM Mali-450 MP4", "ARM Mali-470 MP4", "ARM Mali-G31 MP2", "ARM Mali-G52 MP6",
            "ARM Mali-G57 MP6", "ARM Mali-G77 MP11", "ARM Mali-G68 MP6", "ARM Mali-G76 MP14",

        ]
    elif vendor == "Apple":
        renderers = [
            "Apple A14 Bionic GPU", "Apple A15 Bionic GPU", "Apple A13 Bionic GPU", "Apple A12 Bionic GPU",
            "Apple A11 Bionic GPU", "Apple A10 Fusion GPU", "Apple A9X GPU", "Apple A9 GPU",
            "Apple A8X GPU", "Apple A8 GPU", "Apple A7 GPU", "Apple M1 GPU", "Apple M1 Pro GPU",
            "Apple M1 Max GPU", "Apple M1 Ultra GPU", "Apple M2 GPU", "Apple M2 Pro GPU",
            "Apple M2 Max GPU", "Apple A16 Bionic GPU", "Apple A10X Fusion GPU", "Apple A5X GPU",
            "Apple A6X GPU", "Apple A4 GPU", "Apple M1X GPU", "Apple M1Z GPU", "Apple A3 GPU",
            "Apple A2 GPU", "Apple A1 GPU", "Apple A11X Bionic GPU", "Apple A10X GPU", "Apple M2 Ultra GPU",
            "Apple M3 GPU", "Apple M3 Pro GPU", "Apple M3 Max GPU", "Apple A14X Bionic GPU",
            "Apple A13X Bionic GPU", "Apple A12X Bionic GPU", "Apple A11X Fusion GPU", "Apple M1Z Ultra GPU",
            "Apple A10 Fusion Plus GPU", "Apple A9 Plus GPU", "Apple A8 Plus GPU", "Apple A7X GPU",
            "Apple A6 Plus GPU", "Apple A5 GPU Plus", "Apple M2X GPU", "Apple M3 Ultra GPU",
            "Apple A12Z Bionic GPU", "Apple A15X Bionic GPU", "Apple A16X Bionic GPU", "Apple M4 GPU"
        ]
    else:
        renderers = [
            "Google Inc. ANGLE (NVIDIA GeForce RTX 3060)", "Google Inc. ANGLE (Intel(R) HD Graphics 620)",
            "Google Inc. ANGLE (AMD Radeon RX 570)", "Google Inc. ANGLE (NVIDIA GeForce GTX 1050 Ti)",
            "Google Inc. ANGLE (NVIDIA GeForce GTX 1060)", "Google Inc. ANGLE (Intel(R) UHD Graphics 620)",
            "Google Inc. ANGLE (Intel(R) Iris Plus Graphics 640)", "Google Inc. ANGLE (AMD Radeon RX 580)",
            "Google Inc. ANGLE (NVIDIA GeForce RTX 2080)", "Google Inc. ANGLE (Intel(R) Iris Xe Graphics)",
            "Google Inc. ANGLE (AMD Radeon RX 6900 XT)", "Google Inc. ANGLE (NVIDIA Quadro RTX 4000)",
            "Google Inc. ANGLE (NVIDIA GeForce GTX 1660 Ti)", "Google Inc. ANGLE (NVIDIA Tesla T4)",
            "Google Inc. ANGLE (AMD Radeon RX 5700)", "Google Inc. ANGLE (Intel(R) UHD Graphics 605)",
            "Google Inc. ANGLE (NVIDIA GeForce RTX 3070)", "Google Inc. ANGLE (NVIDIA Quadro P2200)",
            "Google Inc. ANGLE (Intel(R) HD Graphics 630)", "Google Inc. ANGLE (NVIDIA GeForce GTX 1650)",
            "Google Inc. ANGLE (AMD Radeon Pro 5500 XT)", "Google Inc. ANGLE (AMD Radeon Pro W5700)",
            "Google Inc. ANGLE (NVIDIA GeForce RTX 4090)", "Google Inc. ANGLE (NVIDIA Tesla V100)",
            "Google Inc. ANGLE (Intel(R) Iris Pro Graphics 580)", "Google Inc. ANGLE (NVIDIA Quadro M5000)",
            "Google Inc. ANGLE (AMD FirePro W9100)", "Google Inc. ANGLE (NVIDIA Quadro RTX 5000)",
            "Google Inc. ANGLE (AMD Radeon RX Vega 64)", "Google Inc. ANGLE (Intel(R) Iris Xe MAX Graphics)"
        ]

    renderer = random.choice(renderers)

    # 基本信息
    platform_info = f"{vendor} ({renderer});ANGLE ({renderer}"
    if not is_mobile:
        platform_info += "Direct3D11 vs_5_0 ps_5_0, D3D11);WebKit WebGL;WebKit"

    # WebGL 版本
    webgl_version = "WebKit WebGL;WebKit;" + "WebGL 1.0 (OpenGL ES 2.0 Chromium)"
    glsl_version = "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)"
    # 模拟最大纹理尺寸（通常为 8192 或 16384）
    max_texture_size = random.choice([8192, 16384])

    # 模拟支持的 WebGL 扩展
    extensions = [
        "ANGLE_instanced_arrays", "EXT_blend_minmax", "EXT_clip_control", "EXT_color_buffer_half_float",
        "EXT_depth_clamp", "EXT_disjoint_timer_query", "EXT_float_blend", "EXT_frag_depth",
        "EXT_polygon_offset_clamp", "EXT_shader_texture_lod", "EXT_texture_compression_bptc",
        "EXT_texture_compression_rgtc", "EXT_texture_filter_anisotropic", "EXT_texture_mirror_clamp_to_edge",
        "EXT_sRGB", "KHR_parallel_shader_compile", "OES_element_index_uint", "OES_fbo_render_mipmap",
        "OES_standard_derivatives", "OES_texture_float", "OES_texture_float_linear", "OES_texture_half_float",
        "OES_texture_half_float_linear", "OES_vertex_array_object", "WEBGL_blend_func_extended",
        "WEBGL_color_buffer_float", "WEBGL_compressed_texture_s3tc", "WEBGL_compressed_texture_s3tc_srgb",
        "WEBGL_debug_renderer_info", "WEBGL_debug_shaders", "WEBGL_depth_texture", "WEBGL_draw_buffers",
        "WEBGL_lose_context", "WEBGL_multi_draw", "WEBGL_polygon_mode", "EXT_texture_compression_astc",
        "EXT_shader_image_load_store", "EXT_disjoint_timer_query_webgl2", "EXT_texture_norm16",
        "EXT_texture_rg", "EXT_texture_sRGB_decode", "EXT_color_buffer_float", "EXT_float_blend",
        "EXT_frag_depth", "EXT_shader_framebuffer_fetch", "EXT_texture_compression_etc",
        "EXT_texture_compression_latc", "EXT_texture_compression_pvrtc", "EXT_texture_compression_s3tc",
        "KHR_texture_compression_astc_hdr", "KHR_texture_compression_astc_ldr",
        "KHR_texture_compression_astc_sliced_3d",
        "OES_depth32", "OES_draw_buffers_indexed", "OES_element_index_uint", "OES_fbo_render_mipmap",
        "OES_standard_derivatives", "OES_texture_3D", "OES_texture_border_clamp", "OES_texture_float",
        "OES_texture_half_float_linear", "OES_vertex_array_object", "WEBGL_compressed_texture_astc",
        "WEBGL_compressed_texture_etc", "WEBGL_compressed_texture_etc1", "WEBGL_compressed_texture_pvrtc",
        "WEBGL_compressed_texture_s3tc_srgb", "WEBGL_debug_renderer_info", "WEBGL_debug_shaders",
        "WEBGL_depth_texture", "WEBGL_draw_buffers", "WEBGL_lose_context", "WEBGL_multi_draw",
        "WEBGL_multi_draw_instanced", "WEBGL_polygon_offset_clamp", "WEBGL_sRGB", "WEBGL_texture_float",
        "WEBGL_texture_half_float", "WEBGL_vao", "WEBGL_vertex_array_object", "WEBGL2_compressed_texture_astc",
        "WEBGL2_compressed_texture_etc", "WEBGL2_compressed_texture_pvrtc", "WEBGL2_compressed_texture_s3tc",
        "WEBGL2_texture_float_linear", "WEBGL2_texture_half_float_linear", "WEBGL2_vertex_array_object",
        "WEBGL2_draw_buffers_indexed", "WEBGL2_frag_depth", "WEBGL2_shader_framebuffer_fetch",
        "WEBGL2_texture_border_clamp", "WEBGL2_vertex_array_object", "EXT_shader_texture_lod",
        "EXT_texture_filter_anisotropic", "EXT_shader_framebuffer_fetch", "WEBGL_compressed_texture_astc_hdr",
        "WEBGL_compressed_texture_astc_ldr", "WEBGL_compressed_texture_astc_sliced_3d", "WEBGL2_multi_draw_instanced",
        "WEBGL2_multi_draw", "WEBGL_color_buffer_float", "WEBGL_compressed_texture_s3tc",
        "WEBGL_compressed_texture_s3tc_srgb", "EXT_disjoint_timer_query", "EXT_texture_filter_anisotropic_3d",
        "EXT_debug_shaders", "EXT_debug_renderer_info", "OES_texture_half_float_cube_map",
        "WEBGL_compressed_texture_etc2", "WEBGL_compressed_texture_s3tc_srgb", "WEBGL_compressed_texture_pvrtc",
        "WEBGL_debug_renderer_info", "WEBGL_draw_instanced_base_vertex_base_instance",
        "WEBGL_multi_draw_indirect", "WEBGL_multi_draw_instanced_base_vertex_base_instance",
        "WEBGL_multi_draw_indirect_count", "WEBGL_compressed_texture_etc", "WEBGL_compressed_texture_pvrtc_srgb",
        "WEBGL_debug_shaders", "WEBGL_debug_renderer_info", "EXT_debug_shaders", "EXT_debug_renderer_info",
        "WEBGL_debug_texture_info", "WEBGL_debug_vertex_array_info", "WEBGL_debug_buffer_info",
        "WEBGL_debug_framebuffer_info", "WEBGL_debug_shader_info", "WEBGL_debug_program_info",
        "WEBGL_debug_uniform_info", "WEBGL_debug_varying_info", "WEBGL_debug_input_info",
        "WEBGL_debug_output_info", "WEBGL_debug_context_info", "WEBGL_debug_performance_info",
        "WEBGL_debug_memory_info", "WEBGL_debug_pipeline_info", "WEBGL_debug_viewport_info",
        "WEBGL_debug_texture_info", "WEBGL_debug_renderbuffer_info", "WEBGL_debug_fence_info",
        "WEBGL_debug_query_info", "WEBGL_debug_sampler_info", "WEBGL_debug_transform_feedback_info",
        "WEBGL_debug_sync_info", "WEBGL_debug_buffer_info", "WEBGL_debug_shader_info",
        "WEBGL_debug_uniform_info", "WEBGL_debug_varying_info", "WEBGL_debug_shader_compilation_info",
        "WEBGL_debug_renderbuffer_info", "WEBGL_debug_texture_info", "WEBGL_debug_buffer_info",
        "WEBGL_debug_framebuffer_info", "WEBGL_debug_vertex_array_info", "WEBGL_debug_buffer_binding_info",
        "WEBGL_debug_buffer_sub_data_info", "WEBGL_debug_vertex_attrib_pointer_info",
        "WEBGL_debug_vertex_array_binding_info", "WEBGL_debug_vertex_attrib_divisor_info",
        "WEBGL_debug_vertex_attrib_array_pointer_info", "WEBGL_debug_vertex_attrib_array_info",
        "WEBGL_debug_vertex_attrib_array_divisor_info", "WEBGL_debug_vertex_array_binding_info",
        "WEBGL_debug_vertex_attrib_binding_info", "WEBGL_debug_vertex_attrib_format_info",
        "WEBGL_debug_vertex_attrib_stride_info", "WEBGL_debug_vertex_attrib_buffer_info",
        "WEBGL_debug_vertex_attrib_integer_info", "WEBGL_debug_vertex_attrib_normalized_info",
        "WEBGL_debug_vertex_attrib_size_info", "WEBGL_debug_vertex_attrib_type_info",
        "WEBGL_debug_vertex_array_object_info", "WEBGL_debug_vertex_array_binding_info",
        "WEBGL_debug_vertex_array_object_buffer_info", "WEBGL_debug_vertex_array_object_info",
        "WEBGL_debug_vertex_array_binding_info", "WEBGL_debug_vertex_attrib_binding_info",
        "WEBGL_debug_vertex_attrib_buffer_info", "WEBGL_debug_vertex_array_object_info",
        "WEBGL_debug_vertex_array_binding_info", "WEBGL_debug_vertex_attrib_binding_info",
        "WEBGL_debug_vertex_attrib_pointer_info", "WEBGL_debug_vertex_array_binding_info",
        "WEBGL_debug_vertex_attrib_array_buffer_info", "WEBGL_debug_vertex_attrib_format_info",
        "WEBGL_debug_vertex_attrib_normalized_info", "WEBGL_debug_vertex_attrib_integer_info",
        "WEBGL_debug_vertex_attrib_type_info", "WEBGL_debug_vertex_attrib_divisor_info",
        "WEBGL_debug_vertex_attrib_stride_info", "WEBGL_debug_vertex_attrib_array_buffer_info",
        "WEBGL_debug_vertex_attrib_binding_info", "WEBGL_debug_vertex_attrib_divisor_info",
        "WEBGL_debug_vertex_attrib_stride_info", "WEBGL_debug_vertex_attrib_array_buffer_info",
        "WEBGL_debug_vertex_attrib_binding_info", "WEBGL_debug_vertex_attrib_format_info",
        "WEBGL_debug_vertex_attrib_normalized_info", "WEBGL_debug_vertex_attrib_integer_info",
        "WEBGL_debug_vertex_attrib_type_info", "WEBGL_debug_vertex_attrib_size_info",
        "WEBGL_debug_vertex_array_object_info", "WEBGL_debug_vertex_array_binding_info",
        "WEBGL_debug_vertex_array_object_info", "WEBGL_debug_vertex_array_binding_info",
        "WEBGL_debug_vertex_array_binding_info", "WEBGL_debug_vertex_array_binding_info"

    ]

    # 随机选择部分扩展作为支持的扩展
    supported_extensions = random.sample(extensions, k=random.randint(12, len(extensions)))

    # 组合最终的模拟信息
    simulated_info = (
            f"{platform_info};{webgl_version};{glsl_version};{max_texture_size};" +
            ",".join(supported_extensions)
    )

    return simulated_info
