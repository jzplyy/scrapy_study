from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils import gen_attach_excel, get_mongodb_connection, get_mysql_connection, send_email

sql = """
SELECT 
service_email 
FROM 
sbd_cpm.quotation_header 
WHERE
quotation_code = %s
"""

conn = get_mysql_connection()
cursor = conn.cursor()

mongo_client = get_mongodb_connection()
db = mongo_client['spider_tmp']
collection_new = db['cpm_new']
collection_publish = db['cpm_publish']
collection_update = db['cpm_update']

email_item = {}

try:
    for item in collection_publish.find({}):
        quotation_code = item['quotation_code']
        cursor.execute(sql, quotation_code)
        res = cursor.fetchone()
        if not res:
            continue
        email = res[0]
        if not email_item.get(email):
            email_item[email] = {}
        if not email_item[email].get('publish'):
            email_item[email]['publish'] = []
        email_item[email]['publish'].append(quotation_code)

    for item in collection_update.find({}):
        quotation_code = item['quotation_code']
        cursor.execute(sql, quotation_code)
        res = cursor.fetchone()
        if not res:
            continue
        email = res[0]
        if not email_item.get(email):
            email_item[email] = {}
        if not email_item[email].get('update'):
            email_item[email]['update'] = []
        email_item[email]['update'].append(quotation_code)

    for item in collection_new.find({}):
        quotation_code = item['quotation_code']
        cursor.execute(sql, quotation_code)
        res = cursor.fetchone()
        if not res:
            continue
        email = res[0]
        if not email_item.get(email):
            email_item[email] = {}
        if not email_item[email].get('new'):
            email_item[email]['new'] = []
        email_item[email]['new'].append(quotation_code)
finally:
    cursor.close()
    conn.close()
    mongo_client.close()

if not email_item:
    print('--- NO MAIL ---')

for to_email, v in email_item.items():
    update_list = v.get('update')
    new_list = v.get('new')
    publish_list = v.get('publish')
    if update_list:
        try:
            for quotation_code in update_list:
                gen_attach_excel(quotation_code)
            send_email(to_email, update_list, email_type='update')
        except Exception as e:
            print(f'INFORM ERROR:{to_email},{v}')
    if new_list:
        try:
            for quotation_code in new_list:
                gen_attach_excel(quotation_code)
            send_email(to_email, new_list, email_type='new')
        except Exception as e:
            print(f'INFORM ERROR:{to_email},{v}')
    if publish_list:
        try:
            for quotation_code in publish_list:
                gen_attach_excel(quotation_code)
            send_email(to_email, publish_list, email_type='publish')
        except Exception as e:
            print(f'INFORM ERROR:{to_email},{v}')



