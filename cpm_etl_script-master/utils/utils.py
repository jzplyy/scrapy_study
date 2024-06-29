import pymysql
import yaml
import os
import pymongo
import base64
import traceback
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from openpyxl import load_workbook

from . import BASE_DIR, PRIVATE_KEY_PATH


def get_mysql_connection():
    with open(os.path.join(BASE_DIR, 'conf.yml'), 'r') as f:
        conf = f.read()
    params = yaml.load(conf, Loader=yaml.SafeLoader)
    mysql_params = params['mysql']
    conn = pymysql.connect(**mysql_params)
    return conn


def get_mongodb_connection():
    with open(os.path.join(BASE_DIR, 'conf.yml'), 'r') as f:
        conf = f.read()
    params = yaml.load(conf, Loader=yaml.SafeLoader)
    mango_params = params['mongodb']
    client = pymongo.MongoClient(mango_params['uri'])
    return client


def decrypt_data(encrypt_msg, key_path, join_txt='$&%$'):
    # 读取私钥信息
    with open(key_path, 'r') as f:
        data = f.read()
    private_key = RSA.importKey(data)
    cipher = PKCS1_cipher.new(private_key)
    res = []
    for data_part in encrypt_msg.split(join_txt):
        data_part = base64.b64decode(data_part)
        res.append(cipher.decrypt(data_part, 0).decode())
    return "".join(res)


def gene_workbook_insert(quotation_code, workbook, cursor):
    print(f'--- Processing: {quotation_code}.xls [基因合成] ---')
    sheet = workbook['基因合成']
    sheet._current_row = 2
    gene_sql = """
    SELECT 
    qgs.sequence_name,
    qgs.sequence_type,
    qgs.original_sequence,
    qgs.regex_sequence,
    qgs.opted_seq,
    qap.GeneLength,
    qap.IsServicePriority,
    qgs.restriction_enzyme_site_5, 
    NULL, 
    NULL,
    qgs.restriction_enzyme_site_3,
    qgs.is_optimize,
    qgs.species_for_codon_optimization,
    NULL,
    qgs.excluded_restriction_enzyme_site,
    NULL,
    qgs.cloning_vector,
    NULL,
    NULL,
    qgs.vector_resistance,
    NULL,
    qgs.cloning_host ,
    NULL,
    qgs.remark
    FROM sbd_cpm.quotation_gene_synthesis qgs 
    LEFT JOIN sbd_cpm.quotation_amount_period qap
    ON
    qgs.quotation_code = qap.quotation_code 
    AND 
    qgs.sequence_name = qap.SequenceName 
    WHERE 
    qgs.quotation_code = %s
    AND
    qap.type = 'gene'
    ORDER BY 
    qgs.data_id ASC
    """
    cursor.execute(gene_sql, quotation_code)
    for item in cursor.fetchall():
        _item = list(item)
        _item[2] = decrypt_data(item[2], PRIVATE_KEY_PATH) if item[2] else ''
        _item[3] = decrypt_data(item[3], PRIVATE_KEY_PATH) if item[3] else ''
        _item[4] = decrypt_data(item[4], PRIVATE_KEY_PATH) if item[4] else ''
        sheet.append(_item)
    return sheet


def pcr_cloning_workbook_insert(quotation_code, workbook, cursor):
    print(f'--- Processing: {quotation_code}.xls [PCR克隆] ---')
    sheet = workbook['PCR克隆']
    sheet._current_row = 3
    # TODO 其他克隆载体序列
    sql = """
    SELECT 
    s1.target_sequence_name,
    s1.target_sequence,
    s2.template_sequence_name_1,
    s2.template_sequence_1,
    s3.template_sequence_name_2,
    s3.template_sequence_2,
    s4.template_sequence_name_3,
    s4.template_sequence_3,
    NULL,
    s1.cloning_vector_name,
    NULL, # 该载体是否存在于WuXi Bio
    NULL, # 其他克隆载体序列
    s1.vector_resistance, # 载体抗性
    NULL, # 其他抗性
    s1.cloning_site_5,
    NULL, # 其他5'克隆位点
    s1.cloning_site_3,
    NULL, # 其他3'克隆位点
    s1.recombinant_vector_name,
    s1.cloning_host,
    NULL, # 其他克隆宿主
    s1.remark
    FROM (
        SELECT 
        pcl.*,
        pcs.sequence_regex as 'target_sequence'
        FROM 
        sbd_cpm.pcr_cloning_list pcl 
        LEFT JOIN 
        sbd_cpm.pcr_cloning_sequence pcs
        ON
        pcl.data_id = pcs.data_id 
        AND 
        pcl.target_sequence_name = pcs.sequence_name 
    ) s1
    JOIN (
        SELECT 
        pcl.data_id,
        pcl.template_sequence_name_1,
        pcs.sequence_regex as 'template_sequence_1'
        FROM 
        sbd_cpm.pcr_cloning_list pcl 
        LEFT JOIN 
        sbd_cpm.pcr_cloning_sequence pcs
        ON
        pcl.data_id = pcs.data_id 
        AND 
        pcl.template_sequence_name_1 = pcs.sequence_name 
    ) s2
    JOIN (
        SELECT 
        pcl.data_id,
        pcl.template_sequence_name_2,
        pcs.sequence_regex as 'template_sequence_2'
        FROM 
        sbd_cpm.pcr_cloning_list pcl 
        LEFT JOIN 
        sbd_cpm.pcr_cloning_sequence pcs
        ON
        pcl.data_id = pcs.data_id 
        AND 
        pcl.template_sequence_name_2 = pcs.sequence_name 
    ) s3
    JOIN (
        SELECT 
        pcl.data_id,
        pcl.template_sequence_name_3,
        pcs.sequence_regex as 'template_sequence_3'
        FROM 
        sbd_cpm.pcr_cloning_list pcl 
        LEFT JOIN 
        sbd_cpm.pcr_cloning_sequence pcs
        ON
        pcl.data_id = pcs.data_id 
        AND 
        pcl.template_sequence_name_3 = pcs.sequence_name 
    ) s4
    ON 
    s1.data_id = s2.data_id
    AND 
    s1.data_id = s3.data_id
    AND 
    s1.data_id = s4.data_id
    WHERE 
    s1.quotation_code = %s
    ORDER BY 
	s1.target_sequence_name ASC
    """
    cursor.execute(sql, quotation_code)
    for item in cursor.fetchall():
        _item = list(item)
        _item[1] = decrypt_data(item[1], PRIVATE_KEY_PATH) if item[1] else ''
        _item[3] = decrypt_data(item[3], PRIVATE_KEY_PATH) if item[3] else ''
        _item[5] = decrypt_data(item[5], PRIVATE_KEY_PATH) if item[5] else ''
        _item[7] = decrypt_data(item[7], PRIVATE_KEY_PATH) if item[7] else ''
        sheet.append(_item)
    return sheet


def point_mutation_workbook_insert(quotation_code, workbook, cursor):
    print(f'--- Processing: {quotation_code}.xls [点突变] ---')
    sheet = workbook['点突变']
    sheet._current_row = 3
    # TODO 其他克隆载体序列
    sql = """
    SELECT 
    s1.mutation_name,
    s1.mutation_sequence_type,
    s1.mutation_sequence,
    s1.template_name,
    s1.template_sequence_type,
    s2.template_sequence,
    NULL, # 克隆载体名称
    s1.cloning_vector_name,
    NULL, # 该载体是否存在于WuXi Bio
    NULL, # 其他克隆载体序列
    s1.vector_resistance, # 载体抗性
    NULL, # 其他抗性
    s1.cloning_site_5,
    NULL, # 其他5'克隆位点
    s1.cloning_site_3,
    NULL, # 其他3'克隆位点
    s1.cloning_host,
    NULL, # 其他克隆宿主
    s1.remark
    FROM 
    (
        SELECT 
        pml.*,
        pms.template_sequence_regex as 'mutation_sequence'
        FROM 
        sbd_cpm.point_mutation_list pml 
        LEFT JOIN
        sbd_cpm.point_mutation_sequence pms
        ON
        pml.data_id = pms.data_id 
        AND 
        pml.mutation_name = pms.template_name 
    ) s1
    JOIN 
    (
        SELECT 
        pml.data_id ,
        pml.template_name ,
        pms.template_sequence_regex as 'template_sequence'
        FROM 
        sbd_cpm.point_mutation_list pml 
        LEFT JOIN
        sbd_cpm.point_mutation_sequence pms
        ON
        pml.data_id = pms.data_id 
        AND 
        pml.template_name = pms.template_name 
    ) s2
    ON 
    s1.data_id = s2.data_id
    WHERE 
    s1.quotation_code = %s
    ORDER BY 
    s1.mutation_name ASC
    """
    cursor.execute(sql, quotation_code)
    for item in cursor.fetchall():
        _item = list(item)
        _item[2] = decrypt_data(item[2], PRIVATE_KEY_PATH) if item[2] else ''
        _item[5] = decrypt_data(item[5], PRIVATE_KEY_PATH) if item[5] else ''
        sheet.append(_item)
    return sheet


def plasmid_preparation_insert(quotation_code, workbook, cursor):
    print(f'--- Processing: {quotation_code}.xls [质粒制备] ---')
    sheet = workbook['质粒制备']
    sheet._current_row = 2
    sql = """
    SELECT 
    ppl.sample_name,
    ppl.sample_type,
    ppl.preparation_amount,
    ppl.host,
    NULL, # 其它宿主
    ppl.endotoxin_level,
    ppl.buffer_solution,
    ppl.dna_concentration,
    ppl.subpackage_tubes,
    ppl.plasmid_antibiotics, 
    NULL, # 其他抗性
    ppl.plasmid_length_bp,
    ppl.level_plasmid_copy_number,
    ppl.is_sequencing,
    ppl.sequencing_primer,
    pps.theoretical_sequence_name,
    pps.theoretical_sequence
    FROM 
    sbd_cpm.plasmid_preparation_list ppl 
    LEFT JOIN sbd_cpm.plasmid_preparation_sequence pps
    ON
    ppl.data_id = pps.data_id 
    WHERE 
    ppl.quotation_code = %s
    ORDER BY 
    ppl.sample_name ASC 
    """
    cursor.execute(sql, quotation_code)
    for item in cursor.fetchall():
        _item = list(item)
        _item[16] = decrypt_data(item[16], PRIVATE_KEY_PATH) if item[16] else ''
        sheet.append(_item)
    return sheet


def gen_attach_excel(quotation_code):
    excel_template_path = os.path.join(BASE_DIR, 'export_template.xlsx')
    temp_path = os.path.join(BASE_DIR, '_temp')
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)
    workbook = load_workbook(excel_template_path)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        gene_workbook_insert(quotation_code, workbook, cursor)
        pcr_cloning_workbook_insert(quotation_code, workbook, cursor)
        point_mutation_workbook_insert(quotation_code, workbook, cursor)
        plasmid_preparation_insert(quotation_code, workbook, cursor)
        workbook.save(os.path.join(temp_path, f'{quotation_code}.xlsx'))
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        cursor.close()
        conn.close()
        workbook.close()
