import base64
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher


def encrypt_data(msg, key_path, length=200, join_txt='$&%$'):
    """
    1024bit的证书用100， 2048bit的证书用 200
    """
    # 读取公钥信息
    with open(key_path, 'r') as f:
        data = f.read()
    public_key = RSA.importKey(data)
    cipher = PKCS1_cipher.new(public_key)
    res = []
    for i in range(0, len(msg), length):
        data_part = cipher.encrypt(msg[i:i + length].encode())
        data_part = base64.b64encode(data_part).decode()
        res.append(data_part)
    return join_txt.join(res)


def decrypt_data(encrypt_msg, key_path, join_txt='$&%$'):
    # 读取私钥信息
    with open(key_path, 'r') as f:
        data = f.read()
    private_key = RSA.importKey(data)
    cipher = PKCS1_cipher.new(private_key)
    res = []
    for data_part in encrypt_msg.split(join_txt):
        data_part = base64.b64decode(data_part)
        res.append(cipher.decrypt(data_part, 0).decode())
    return "".join(res)


if __name__ == '__main__':
    msg = "test..."
    public_key_path = '../utils/public_key.pem'
    private_key_path = '../utils/private_key.pem'
    encrypt_text = encrypt_data(msg, public_key_path)  # 加密
    decrypt_text = decrypt_data(encrypt_text, private_key_path)  # 解密
    print(encrypt_text)
    print(decrypt_text)
    print(decrypt_text == msg)
