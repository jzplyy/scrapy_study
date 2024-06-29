from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils import get_mysql_connection

sql_delete = """
DELETE FROM sbd_cpm.plasmid_preparation_sequence;
"""

sql_reset_id = """
ALTER TABLE sbd_cpm.plasmid_preparation_sequence auto_increment = 1;
"""

sql_insert = """
INSERT INTO sbd_cpm.plasmid_preparation_sequence 
(cpm_id,
quotation_code,
active_version,
data_id,
theoretical_sequence_name,
theoretical_sequence,
remark)
SELECT * FROM (
	SELECT 
	qap.id as cpm_id,
	qap.quotation_code,
	qap.active_version,
	qap.data_id,
	qap.theoretical_sequence_name,
	qap.theoretical_sequence,
	qap.remark
	FROM spider.cpm_plasmid_preparation_sequence qap
	RIGHT JOIN (
		SELECT 
		quotation_code, 
		MAX(`_job_start_time` ) AS _job_start_time
		FROM spider.cpm_plasmid_preparation_sequence 
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
