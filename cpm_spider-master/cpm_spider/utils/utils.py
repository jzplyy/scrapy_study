import base64
import pymysql
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher

from cpm_spider.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


def aes_cipher(data, key='z2QkCU%&3lec8F2m', replacer='edcedc'):
    aes = AES.new(key.encode('utf-8'), AES.MODE_ECB)  # 先用秘钥加密
    pad_pkcs7 = pad(data.encode('utf-8'), AES.block_size, style='pkcs7')  # 选择pkcs7补全
    encrypt_aes = aes.encrypt(pad_pkcs7)
    # 加密结果
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 解码
    encrypted_text = encrypted_text.replace("\n", "").replace("/", replacer)
    return encrypted_text


def query_seed_from_quotation_list():
    """
    直接从cpm_quotation_list表中查询种子数据
    :return: id,quotation_code
    """
    sql = """
        SELECT
        cqlm.id,cqlm.quotation_code 
        FROM spider.cpm_quotation_list cqlm
        RIGHT JOIN  (
            SELECT 
            cql._job_id ,max(cql._job_start_time ) as _latest_job_time
            FROM spider.cpm_quotation_list cql
            GROUP BY cql._job_id
            ORDER BY _latest_job_time DESC
            LIMIT 1
        ) cqlz
        ON
        cqlm._job_id  = cqlz._job_id
        WHERE
        cqlm.quotation_code NOT LIKE 'Domain-%'
        AND 
        cqlm.quotation_code NOT LIKE '-%'
    """
    conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD,
                           database='spider')
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    column_number_list = []
    for row in result:
        column_number_list.append((row[0], row[1]))
    return column_number_list


def query_seed_from_quotation_header():
    """
    直接从cpm_quotation_list表中查询种子数据
    :return: id,quotation_code
    """
    sql = """
        SELECT
        cqlm.id,cqlm.quotation_code,cqlm.active_version 
        FROM spider.cpm_quotation_header cqlm
        RIGHT JOIN  (
            SELECT 
            cql._job_id ,max(cql._job_start_time ) as _latest_job_time
            FROM spider.cpm_quotation_header cql
            GROUP BY cql._job_id
            ORDER BY _latest_job_time DESC
            LIMIT 1
        ) cqlz
        ON
        cqlm._job_id  = cqlz._job_id
        WHERE
        cqlm.quotation_code NOT LIKE 'Domain-%'
        AND 
        cqlm.quotation_code NOT LIKE '-%'
    """
    conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD,
                           database='spider')
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    column_number_list = []
    for row in result:
        column_number_list.append((row[0], row[1], row[2]))
    return column_number_list


def __gen_rsa_keys():
    random_generator = Random.new().read  # 生成随机偏移量
    rsa = RSA.generate(2048, random_generator)  # 生成一个私钥
    # 生成私钥
    private_key = rsa.exportKey()  # 导出私钥
    # 生成公钥
    public_key = rsa.publickey().exportKey()  # 生成私钥所对应的公钥

    with open('private_key.pem', 'wb') as f:
        f.write(private_key)

    with open('public_key.pem', 'wb') as f:
        f.write(public_key)


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


def get_account_pwd():
    sql = """
    SELECT * FROM spider.account WHERE domain='cpm'
    """
    conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD,
                           database='spider')
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[2], result[3]
