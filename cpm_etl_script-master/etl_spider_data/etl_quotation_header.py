from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils import get_mysql_connection

sql_delete = """
DELETE FROM sbd_cpm.quotation_header;
"""

sql_reset_id = """
ALTER TABLE sbd_cpm.quotation_header auto_increment = 1;
"""

sql_insert = """
INSERT INTO sbd_cpm.quotation_header 
(cpm_id,quotation_code,active_version,customer,customer_contacts,customer_phone,customer_email,confirm_time,service_contacts,service_phone,service_email,publish_time)
SELECT * FROM (
	SELECT 
	cqh.id as cpm_id,
	cqh.quotation_code,
	cqh.active_version, 
	cqh.customer,
	cqh.customer_contacts,
	cqh.customer_phone,
	cqh.customer_email,
	CAST(IF(cqh.confirm_time='', null , cqh.confirm_time) AS datetime) AS confirm_time,
	cqh.service_contacts,
	cqh.service_phone,
	cqh.service_email,
	CAST(IF(cqh.publish_time='', null , cqh.publish_time) AS datetime) AS publish_time
	FROM spider.cpm_quotation_header cqh
	RIGHT JOIN (
		SELECT 
		quotation_code, 
		MAX(`_job_start_time` ) AS _job_start_time
		FROM spider.cpm_quotation_header 
		WHERE quotation_code IS NOT NULL 
		GROUP BY quotation_code
	) cqhi
	 ON
	 cqh.quotation_code = cqhi.quotation_code
	 AND
	 cqh._job_start_time = cqhi._job_start_time
	 WHERE 
	 cqh.quotation_code NOT LIKE 'Domain-%'
	 AND 
	 cqh.quotation_code NOT LIKE '-%'
) AS source;
"""

conn = get_mysql_connection()
cursor = conn.cursor()
try:
    print('start delete...')
    cursor.execute(sql_delete)
    print('delete done!')
    cursor.execute(sql_reset_id)
    print('start insert...')
    cursor.execute(sql_insert)
    print('insert done!')
    conn.commit()
except Exception as e:
    conn.rollback()
    raise e
finally:
    cursor.close()
    conn.close()
