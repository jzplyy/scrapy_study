from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils import get_mongodb_connection, get_mysql_connection

filter_sql = """
SELECT
nsp.quotation_status as new_status,
nsp.quotation_code,
src.quotation_status as old_status,
src.quotation_code
FROM (
	SELECT 
	cql.id as cpm_id,
	cql.quotation_code, 
	cql.user_name,
	cql.quotation_status,
	cql.wbp_code,
	cql.archive_date
	FROM spider.cpm_quotation_list cql
	RIGHT JOIN (
		SELECT 
		quotation_code, 
		MAX(`_job_start_time` ) as _job_start_time
		FROM spider.cpm_quotation_list 
		WHERE quotation_code IS NOT NULL 
		GROUP BY quotation_code
	) cqli
	 ON
	 cql.quotation_code = cqli.quotation_code
	 AND
	 cql._job_start_time = cqli._job_start_time
	 WHERE 
	 cql.quotation_code NOT LIKE 'Domain-%'
	 AND 
	 cql.quotation_code NOT LIKE '-%'
) AS nsp
LEFT OUTER JOIN sbd_cpm.quotation_list AS src
ON
nsp.quotation_code = src.quotation_code 
WHERE 
src.quotation_code is NULL # 新订单
OR 
(
nsp.quotation_status != src.quotation_status
AND 
nsp.quotation_status >= 3
)
"""
conn = get_mysql_connection()
cursor = conn.cursor()
cursor.execute(filter_sql)
new_quotation_list = []  # 新增.1
publish_quotation_list = []  # 发布.3
update_quotation_list = []  # 确认.4

for item in cursor.fetchall():
    if item[3] is None and item[0] not in ['3', '4']:
        new_quotation_list.append(item[1])
    else:
        if item[0] == '3':
            publish_quotation_list.append(item[1])
        elif item[0] == '4':
            update_quotation_list.append(item[1])
cursor.close()
conn.close()


mongo_client = get_mongodb_connection()
db = mongo_client['spider_tmp']

collection_new = db['cpm_new']
collection_new.delete_many({})
if new_quotation_list:
    collection_new.insert_many([{'quotation_code': item} for item in new_quotation_list])

collection_new = db['cpm_publish']
collection_new.delete_many({})
if publish_quotation_list:
    collection_new.insert_many([{'quotation_code': item} for item in publish_quotation_list])

collection_update = db['cpm_update']
collection_update.delete_many({})
if update_quotation_list:
    collection_update.insert_many([{'quotation_code': item} for item in update_quotation_list])

mongo_client.close()

if len(new_quotation_list) == 0 and len(update_quotation_list) == 0:
    exit(4)
