from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils import get_mysql_connection

sql_delete = """
DELETE FROM sbd_cpm.plasmid_preparation_list;
"""

sql_reset_id = """
ALTER TABLE sbd_cpm.plasmid_preparation_list auto_increment = 1;
"""

sql_insert = """
INSERT INTO sbd_cpm.plasmid_preparation_list 
(cpm_id,
quotation_code,
active_version,
data_id,
sample_name,
sample_type,
preparation_amount,
host,
endotoxin_level,
buffer_solution,
dna_concentration,
subpackage_tubes,
plasmid_antibiotics,
plasmid_length_bp,
level_plasmid_copy_number,
is_sequencing,
sequencing_primer,
remark)
SELECT * FROM (
	SELECT 
	qap.id as cpm_id,
	qap.quotation_code,
	qap.active_version,
	qap.data_id,
	qap.sample_name,
	qap.sample_type,
	qap.preparation_amount,
	qap.host,
	qap.endotoxin_level,
	qap.buffer_solution,
	qap.dna_concentration,
	qap.subpackage_tubes,
	qap.plasmid_antibiotics,
	qap.plasmid_length_bp,
	qap.level_plasmid_copy_number,
	qap.is_sequencing,
	qap.sequencing_primer,
	qap.remark
	FROM spider.cpm_plasmid_preparation_list qap
	RIGHT JOIN (
		SELECT 
		quotation_code, 
		MAX(`_job_start_time` ) AS _job_start_time
		FROM spider.cpm_plasmid_preparation_list 
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
