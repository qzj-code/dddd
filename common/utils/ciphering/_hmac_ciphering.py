"""
Module: _hmac
Author: Ciwei
Date: 2024-10-03

Description: 
    This module provides functionalities for ...
"""
import base64
import hmac


class HmacCiphering(object):

    @staticmethod
    def encrypt(key: str, message: str, digest="sha256") -> str:
        hmac_instance = hmac.new(key.encode(), message.encode(), digest)
        message_digest = hmac_instance.digest()
        return base64.b64encode(message_digest).decode('utf-8')
