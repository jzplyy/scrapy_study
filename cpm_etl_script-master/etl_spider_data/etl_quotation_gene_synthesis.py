from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils import get_mysql_connection

sql_delete = """
DELETE FROM sbd_cpm.quotation_gene_synthesis;
"""

sql_reset_id = """
ALTER TABLE sbd_cpm.quotation_gene_synthesis auto_increment = 1;
"""

sql_insert = """
INSERT INTO sbd_cpm.quotation_gene_synthesis 
(
cpm_id,quotation_code,active_version,data_id,sequence_name,sequence_type,is_optimize,original_sequence,regex_sequence,opted_seq,
restriction_enzyme_site_5,restriction_enzyme_site_3,is_codon_optimization,species_for_codon_optimization,excluded_restriction_enzyme_site,cloning_vector,cloning_host,remark
)
SELECT
cpm_id,quotation_code,active_version,data_id,sequence_name,sequence_type,is_optimize,original_sequence,regex_sequence,opted_seq,
restriction_enzyme_site_5,restriction_enzyme_site_3,is_codon_optimization,species_for_codon_optimization,excluded_restriction_enzyme_site,cloning_vector,cloning_host,remark
FROM (
	SELECT 
	cql.id as cpm_id,
	cql.quotation_code,
	cql.active_version,
	cql.data_id,
	cql.sequence_name,
	cql.sequence_type,
	cql.is_optimize,
	cql.original_sequence,
	cql.regex_sequence,
	cql.opted_seq
	FROM spider.cpm_quotation_gene_synthesis cql
	RIGHT JOIN (
		SELECT 
		quotation_code, 
		MAX(`_job_start_time` ) as _job_start_time
		FROM spider.cpm_quotation_gene_synthesis 
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
) AS p1
LEFT JOIN (
	SELECT 
	cqg.data_id AS did,
	cqg.restriction_enzyme_site_5,
	cqg.restriction_enzyme_site_3,
	cqg.is_codon_optimization,
	cqg.species_for_codon_optimization,
	cqg.excluded_restriction_enzyme_site,
	cqg.cloning_vector,
	cqg.cloning_host,
	cqg.remark 
	FROM spider.cpm_quotation_gene_synthesis_part2 cqg 
	RIGHT JOIN (
		SELECT
		quotation_code, 
		MAX(`_job_start_time` ) as _job_start_time
		FROM spider.cpm_quotation_gene_synthesis_part2 
		WHERE quotation_code IS NOT NULL 
		GROUP BY quotation_code
	) cqgi
	ON 
	cqg.quotation_code = cqgi.quotation_code
	AND 
	cqg.`_job_start_time` = cqgi.`_job_start_time`
	WHERE 
	cqg.quotation_code NOT LIKE 'Domain-%'
	AND 
	cqg.quotation_code NOT LIKE '-%'
) AS p2
ON p1.data_id = p2.did;
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
