from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils import get_mysql_connection

sql_delete = """
DELETE FROM sbd_cpm.point_mutation_list;
"""

sql_reset_id = """
ALTER TABLE sbd_cpm.point_mutation_list auto_increment = 1;
"""

sql_insert = """
INSERT INTO sbd_cpm.point_mutation_list 
(cpm_id,
quotation_code,
active_version,
data_id,
mutation_name,
mutation_sequence_type,
template_name,
template_sequence_type,
cloning_vector_name,
cloning_site_5,
cloning_site_3,
cloning_host,
match_info,
is_error,
error_msg,
remark)
SELECT * FROM (
	SELECT 
	qap.id as cpm_id,
	qap.quotation_code,
	qap.active_version,
	qap.data_id,
	qap.mutation_name,
	qap.mutation_sequence_type,
	qap.template_name,
	qap.template_sequence_type,
	qap.cloning_vector_name,
	qap.cloning_site_5,
	qap.cloning_site_3,
	qap.cloning_host,
	qap.match_info,
	qap.is_error,
	qap.error_msg,
	qap.remark
	FROM spider.cpm_point_mutation_list qap
	RIGHT JOIN (
		SELECT 
		quotation_code, 
		MAX(`_job_start_time` ) AS _job_start_time
		FROM spider.cpm_point_mutation_list 
		WHERE quotation_code IS NOT NULL 
		GROUP BY quotation_code
	) qapi
	 ON
	 qap.quotation_code = qapi.quotation_code
	 AND
	 qap._job_start_time = qapi._job_start_time
	 WHERE 
	 qap.quotation_code NOT LIKE 'Domain-%'
	 AND 
	 qap.quotation_code NOT LIKE '-%'
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
