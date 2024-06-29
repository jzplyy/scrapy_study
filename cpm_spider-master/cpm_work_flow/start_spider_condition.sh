#!/bin/sh
docker exec cpm_etl_script python etl_spider_data/etl_new_data_from_quotation_list.py
res=$?
echo "python script return: $res"
echo "{\"res\":$res}" > $JOB_OUTPUT_PROP_FILE