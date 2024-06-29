from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils import get_mysql_connection

sql_delete = """
DELETE FROM sbd_cpm.quotation_amount_period;
"""

sql_reset_id = """
ALTER TABLE sbd_cpm.quotation_header auto_increment = 1;
"""

sql_insert = """
INSERT INTO sbd_cpm.quotation_amount_period 
(cpm_id,quotation_code,active_version,SequenceName,ServicePriority,`type`,PreparationAmount,IsServicePriority,EndotoxinLevel,GeneLength,IsCodonOptimization,unit_price,days)
SELECT * FROM (
	SELECT 
	qap.id as cpm_id,
	qap.quotation_code,
	qap.active_version,
	qap.SequenceName,
	qap.ServicePriority,
	qap.`type`,
	qap.PreparationAmount,
	qap.IsServicePriority,
	qap.EndotoxinLevel,
	IF(qap.GeneLength='NA',null,qap.GeneLength) AS GeneLength,
	qap.IsCodonOptimization,
	REPLACE(JSON_EXTRACT(qap.Result,'$.price'),'"','') as unit_price,
	REPLACE(JSON_EXTRACT(qap.Result,'$.period'),'"','') as days
	FROM spider.cpm_quotation_amount_period qap
	RIGHT JOIN (
		SELECT 
		quotation_code, 
		MAX(`_job_start_time` ) AS _job_start_time
		FROM spider.cpm_quotation_amount_period 
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
