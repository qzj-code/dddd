import base64

from Crypto.Cipher import DES

from common.errors import ServiceError, ServiceStateEnum


class DesCiphering:
    BLOCK_SIZE = 8  # DES 使用固定的块大小为 8 字节

    @classmethod
    def pad(cls, data: bytes) -> bytes:
        """
        使用零填充至 8 字节的倍数
        Args:
            data:

        Returns:

        """
        padding_length = cls.BLOCK_SIZE - (len(data) % cls.BLOCK_SIZE)
        return data + b'\x00' * padding_length

    @classmethod
    def validate_key(cls, key: str) -> bytes:
        """
        验证密钥长度
        Args:
            key:

        Returns:

        """
        key_bytes = key.encode()
        if len(key_bytes) != cls.BLOCK_SIZE:
            raise ServiceError(ServiceStateEnum.INVALID_DATA, "密钥长度必须为8字节")
        return key_bytes

    @classmethod
    def encrypt(cls, key: str, data: str) -> str:
        """
        DES 加密
        Args:
            key: 密钥，必须为 8 字节
            data: 明文数据

        Returns:
        Base64 编码的加密数据
        """
        key_bytes = cls.validate_key(key)
        cipher = DES.new(key_bytes, DES.MODE_ECB)

        # 填充并加密
        padded_data = cls.pad(data.encode())
        encrypted_data = cipher.encrypt(padded_data)

        # 转为 Base64
        return base64.b64encode(encrypted_data).decode()

    @classmethod
    def decrypt(cls, key: str, encrypted_data: str) -> str:
        """
        DES解密
        Args:
            key: 密钥，必须为 8 字节
            encrypted_data: Base64 编码的加密数据

        Returns:
            解密后的明文
        """
        key_bytes = cls.validate_key(key)
        cipher = DES.new(key_bytes, DES.MODE_ECB)

        # 解码 Base64 并解密
        encrypted_data_bytes = base64.b64decode(encrypted_data)
        decrypted_data = cipher.decrypt(encrypted_data_bytes)

        # 去填充并返回解密数据
        return decrypted_data.rstrip(b'\x00').decode()

