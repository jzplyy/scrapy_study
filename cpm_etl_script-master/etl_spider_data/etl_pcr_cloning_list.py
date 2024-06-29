from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils import get_mysql_connection

sql_delete = """
DELETE FROM sbd_cpm.pcr_cloning_list;
"""

sql_reset_id = """
ALTER TABLE sbd_cpm.pcr_cloning_list auto_increment = 1;
"""

sql_insert = """
INSERT INTO sbd_cpm.pcr_cloning_list 
(cpm_id,
quotation_code,
active_version,
data_id,
target_sequence_name,
template_sequence_name_1,
template_sequence_name_2,
template_sequence_name_3,
cloning_vector_name,
cloning_site_5,
cloning_site_3,
recombinant_vector_name,
cloning_host,
is_error,
error_msg,
remark)
SELECT * FROM (
	SELECT 
	qap.id as cpm_id,
	qap.quotation_code,
	qap.active_version,
	qap.data_id,
	qap.target_sequence_name,
	qap.template_sequence_name_1,
	qap.template_sequence_name_2,
	qap.template_sequence_name_3,
	qap.cloning_vector_name,
	qap.cloning_site_5,
	qap.cloning_site_3,
	qap.recombinant_vector_name,
	qap.cloning_host,
	qap.is_error,
	qap.error_msg,
	qap.remark
	FROM spider.cpm_pcr_cloning_list qap
	RIGHT JOIN (
		SELECT 
		quotation_code, 
		MAX(`_job_start_time` ) AS _job_start_time
		FROM spider.cpm_pcr_cloning_list 
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
