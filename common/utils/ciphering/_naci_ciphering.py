from nacl import public, utils, bindings
import base64


class NaciCiphering:

    @staticmethod
    def encrypt_model(model, fields_to_encrypt, server_public_key_base64):
        nonce = utils.random(public.Box.NONCE_SIZE)
        client_private_key, client_public_key = NaciCiphering.generate_client_keypair()
        server_public_key = public.PublicKey(base64.b64decode(server_public_key_base64))

        for field in fields_to_encrypt:
            if field in model:
                model[field] = NaciCiphering.get_encrypted_data(model[field], nonce, client_private_key,
                                                                server_public_key)

        model['CryptoPayload'] = {
            'Nonce': base64.b64encode(nonce).decode('utf-8'),
            'ClientPublicKey': base64.b64encode(client_public_key.encode()).decode('utf-8')
        }

        return model

    @staticmethod
    def generate_client_keypair():
        client_public_key_bytes, client_private_key_bytes = bindings.crypto_box_keypair()
        public_key = public.PublicKey(client_public_key_bytes)
        private_key = public.PrivateKey(client_private_key_bytes)
        return private_key, public_key

    @staticmethod
    def get_encrypted_data(message, nonce, client_private_key, server_public_key):
        box = public.Box(client_private_key, server_public_key)
        encrypted = box.encrypt(message.encode('utf-8'), nonce)
        return base64.b64encode(encrypted.ciphertext).decode('utf-8')
