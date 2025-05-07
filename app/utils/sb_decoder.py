from base64 import b64decode
from Crypto.Cipher import DES3
from Crypto.Util.Padding import unpad

def decode_data(encoded_str):
    try:
        if encoded_str:
            encoded_str = encoded_str.replace(' ', '+')
            input_bytes = b64decode(encoded_str)

            key = b"sub1-9ar1-12tim2"
            cipher = DES3.new(key, DES3.MODE_ECB)
            decrypted = cipher.decrypt(input_bytes)
            unpadded = unpad(decrypted, DES3.block_size)

            return unpadded.decode('utf-8')
        else:
            return ""
    except Exception as e:
        return ""