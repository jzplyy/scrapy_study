import os.path
import sys
from pathlib import Path
import pandas as pd
import traceback

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils import get_mysql_connection

file_record_sql = """
SELECT 
cqh.id,
cqh.quotation_code,
cqh.file_path 
FROM spider.cpm_admin_quotation_file cqh 
RIGHT JOIN (
	SELECT 
	quotation_code, 
	MAX(`_job_start_time` ) AS _job_start_time
	FROM spider.cpm_admin_quotation_file 
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
"""

update_gene_sql = """
UPDATE sbd_cpm.quotation_gene_synthesis 
SET 
vector_resistance = %s
WHERE 
quotation_code = %s
AND 
sequence_name  = %s
"""

update_pcr_sql = """
UPDATE sbd_cpm.pcr_cloning_list 
SET 
vector_resistance = %s
WHERE 
quotation_code = %s
AND 
target_sequence_name  = %s
"""

update_pm_sql = """
UPDATE sbd_cpm.point_mutation_list 
SET 
vector_resistance = %s
WHERE 
quotation_code = %s
AND 
mutation_name  = %s
"""

BASE_DIR = '/cpm_etl/_temp'

conn = get_mysql_connection()
cursor = conn.cursor()
print('start search...')
cursor.execute(file_record_sql)


def process_gen(file_path, quotation_code):
    df = pd.read_excel(file_path, header=1, sheet_name='基因合成')
    col_name = '载体抗性*'
    if col_name not in df.columns:
        print(f'ERROR: {col_name} NOT IN {quotation_code}:基因合成 ')
        return
    update_data = []
    for _, row in df.iterrows():
        _sequence_name = row['序列名称* ']
        _vr = row['载体抗性*']
        data = (_vr, quotation_code, _sequence_name)
        update_data.append(data)
    return update_data


def process_pcr(file_path, quotation_code):
    df = pd.read_excel(file_path, header=2, sheet_name='PCR克隆')
    col_name = '载体抗性*'
    if col_name not in df.columns:
        print(f'ERROR: {col_name} NOT IN {quotation_code}:PCR克隆')
        return
    update_data = []
    for _, row in df.iterrows():
        _sequence_name = row['目标序列名称*']
        _vr = row['载体抗性*']
        data = (_vr, quotation_code, _sequence_name)
        update_data.append(data)
    return update_data


def process_pm(file_path, quotation_code):
    df = pd.read_excel(file_path, header=2, sheet_name='点突变')
    col_name = '载体抗性* '
    if col_name not in df.columns:
        print(f'ERROR: {col_name} NOT IN {quotation_code}:点突变')
        return
    update_data = []
    for _, row in df.iterrows():
        _sequence_name = row['突变名称* ']
        _vr = row[col_name]
        data = (_vr, quotation_code, _sequence_name)
        update_data.append(data)
    return update_data

for item in cursor.fetchall():
    id = item[0]
    quotation_code = item[1]
    file_path = os.path.join(BASE_DIR, item[2])
    print(f'start process {file_path}')
    try:
        gene_update_data = process_gen(file_path, quotation_code)
        if gene_update_data:
            cursor.executemany(update_gene_sql, gene_update_data)
            conn.commit()
    except Exception as e:
        print(f'[gen]ERROR: {file_path}')
        traceback.print_exc()
    try:
        pcr_update_data = process_pcr(file_path, quotation_code)
        if pcr_update_data:
            cursor.executemany(update_pcr_sql, pcr_update_data)
            conn.commit()
    except Exception as e:
        print(f'[pcr]ERROR: {file_path}')
        traceback.print_exc()
    try:
        pm_update_data = process_pm(file_path, quotation_code)
        if pm_update_data:
            cursor.executemany(update_pm_sql, pm_update_data)
            conn.commit()
    except Exception as e:
        print(f'[pm]ERROR: {file_path}')
        traceback.print_exc()

cursor.close()
conn.close()
