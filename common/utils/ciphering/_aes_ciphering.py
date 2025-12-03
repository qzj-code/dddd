"""
Module: _aes_util
Author: Ciwei
Date: 2024-10-04

Description: 
    This module provides functionalities for ...
"""
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class AesCiphering:
    # MODE_ECB = 1  #: Electronic Code Book (:ref:`ecb_mode`)
    # MODE_CBC = 2  #: Cipher-Block Chaining (:ref:`cbc_mode`)
    # MODE_CFB = 3  #: Cipher Feedback (:ref:`cfb_mode`)
    # MODE_OFB = 5  #: Output Feedback (:ref:`ofb_mode`)
    # MODE_CTR = 6  #: Counter mode (:ref:`ctr_mode`)
    # MODE_OPENPGP = 7  #: OpenPGP mode (:ref:`openpgp_mode`)
    # MODE_CCM = 8  #: Counter with CBC-MAC (:ref:`ccm_mode`)
    # MODE_EAX = 9  #: :ref:`eax_mode`
    # MODE_SIV = 10  #: Synthetic Initialization Vector (:ref:`siv_mode`)
    # MODE_GCM = 11  #: Galois Counter Mode (:ref:`gcm_mode`)
    # MODE_OCB = 12  #: Offset Code Book (:ref:`ocb_mode`)

    @staticmethod
    def encrypt(data: bytes, key: bytes, iv: bytes, mode) -> bytes:
        padded_plain_text = pad(data, AES.block_size)

        # 创建 AES CBC 加密器
        if mode == 1:
            cipher = AES.new(key, mode)
        else:
            cipher = AES.new(key, mode, iv)

        # 加密明文
        cipher_text = cipher.encrypt(padded_plain_text)
        return cipher_text

    @staticmethod
    def decrypt(data: bytes, key: bytes, iv: bytes, mode) -> bytes:
        # 创建 AES 解密器（判断是否使用 iv）
        if mode == AES.MODE_ECB:
            cipher = AES.new(key, mode)
        else:
            cipher = AES.new(key, mode, iv)

        # 解密密文
        decrypted_data = cipher.decrypt(data)

        # 移除填充并返回明文
        plain_text = unpad(decrypted_data, AES.block_size)
        return plain_text

    @staticmethod
    def encrypt_ecb(key, data):
        if not key or not data:
            return ""

        # Base64 解码密钥
        key = base64.b64decode(key)

        # AES-ECB 加密，PKCS7 填充
        cipher = AES.new(key, AES.MODE_ECB)
        padded_data = pad(data.encode('utf-8'), AES.block_size, style='pkcs7')
        encrypted = cipher.encrypt(padded_data)

        # 返回 Base64 编码的密文
        return base64.b64encode(encrypted).decode('utf-8')

    @staticmethod
    def decrypt_ecb(e: str, encrypted_text: str) -> str:
        if not e or not encrypted_text:
            return ""

        key = base64.b64decode(e)
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_data = base64.b64decode(encrypted_text)
        decrypted = cipher.decrypt(encrypted_data)
        # 去除 PKCS7 填充
        return unpad(decrypted, AES.block_size, style='pkcs7').decode('utf-8')
