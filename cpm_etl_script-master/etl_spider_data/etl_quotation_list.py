from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils import get_mysql_connection

sql_delete = """
DELETE FROM sbd_cpm.quotation_list;
"""

sql_reset_id = """
ALTER TABLE sbd_cpm.quotation_list auto_increment = 1;
"""

sql_insert = """
INSERT INTO sbd_cpm.quotation_list 
(cpm_id,quotation_code,user_name,quotation_status,wbp_code,archive_date)
SELECT * FROM (
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
