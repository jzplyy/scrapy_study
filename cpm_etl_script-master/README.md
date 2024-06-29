# CPM爬虫数据ETL
> 这是对CPM爬虫数据做清洗整合的一系列脚本，任务通过[Azkaban 任务调度平台](http://10.13.123.147:8081/) 调度    
> 数据库配置在：`./utils/conf.yml`  
> <b>FLOW名称</b>代表在 Azkaban workflow 中的名称

## 部署信息
- 部署机器：10.13.123.147 
- docker容器：cpm_etl_script
- 部署路径：/opt/projects/cpm_etl_script/

## 本地部署
```bash
pip install -r requirements.txt
```

## 更新线上环境

##### 后端项目Git commit & push

##### 服务器更新项目代码
```bash
# 拉取项目代码
cd {部署路径}
git pull
```

# 脚本说明

## 获取新数据
- 脚本：etl_new_data_from_quotation_list.py
- FLOW名称：etl_new_data_from_quotation_list
- 获取范围：
  - 新数据
  - 报价状态为“已发布”或“已确认”的数据
- 如果没有新数据FLOW会停止在这一步  

```bash
# command
sh cpm_work_flow/start_spider_condition.sh
```

## 报价单 - 列表页数据ETL
- 脚本：etl_quotation_list.py
- FLOW名称：etl_quotation_List
- 数据表：sbd_cpm.quotation_list  

```bash
# command
docker exec cpm_etl_script python etl_spider_data/etl_quotation_list.py
```

## 报价单 - 首页数据ETL
- 脚本：etl_quotation_header.py
- FLOW名称：etl_quotation_header
- 数据表：sbd_cpm.quotation_header  

```bash
# command
docker exec cpm_etl_script python etl_spider_data/etl_quotation_header.py
```

## 报价单 - 合同金额和周期数据ETL
- 脚本：etl_quotation_amount_period.py
- FLOW名称：etl_quotation_amount_period
- 数据表：sbd_cpm.quotation_amount_period  

```bash
# command
docker exec cpm_etl_script python etl_spider_data/etl_quotation_amount_period.py
```

## 报价单 - 点突变 - 序列信息数据ETL
- 脚本：etl_point_mutation_sequence.py
- FLOW名称：etl_point_mutation_sequence
- 数据表：sbd_cpm.point_mutation_sequence  

```bash
# command
docker exec cpm_etl_script python etl_spider_data/etl_point_mutation_sequence.py
```

## 报价单 - 点突变 - 列表数据ETL
- 脚本：etl_point_mutation_list.py
- FLOW名称：etl_point_mutation_list
- 数据表：sbd_cpm.point_mutation_list  

```bash
# command
docker exec cpm_etl_script python etl_spider_data/etl_point_mutation_list.py
```

## 报价单 - 质粒制备 - 序列信息数据ETL
- 脚本：etl_plasmid_preparation_sequence.py
- FLOW名称：etl_plasmid_preparation_sequence
- 数据表：sbd_cpm.plasmid_preparation_sequence  

```bash
# command
docker exec cpm_etl_script python etl_spider_data/etl_plasmid_preparation_sequence.py
```

## 报价单 - 质粒制备 - 列表数据ETL
- 脚本：etl_plasmid_preparation_list.py
- FLOW名称：etl_plasmid_preparation_list
- 数据表：sbd_cpm.plasmid_preparation_list  

```bash
# command
docker exec cpm_etl_script python etl_spider_data/etl_plasmid_preparation_list.py
```

## 报价单 - PCR克隆 - 序列信息数据ETL
- 脚本：etl_pcr_cloning_sequence.py
- FLOW名称：etl_pcr_cloning_sequence
- 数据表：sbd_cpm.pcr_cloning_sequence  

```bash
# command
docker exec cpm_etl_script python etl_spider_data/etl_pcr_cloning_sequence.py
```

## 报价单 - PCR克隆 - 列表数据ETL
- 脚本：etl_pcr_cloning_list.py
- FLOW名称：etl_pcr_cloning_list
- 数据表：sbd_cpm.pcr_cloning_list  

```bash
# command
docker exec cpm_etl_script python etl_spider_data/etl_pcr_cloning_list.py
```

## 报价单 - 基因合成数据ETL
- 脚本：etl_quotation_gene_synthesis.py
- FLOW名称：etl_quotation_gene_synthesis
- 数据表：sbd_cpm.quotation_gene_synthesis  

```bash
# command
docker exec cpm_etl_script python etl_spider_data/etl_quotation_gene_synthesis.py
```

## 管理后台 - 获取用户上传的载体抗性
- 脚本：etl_admin_quotation_file.py
- FLOW名称：etl_admin_quotation_file
- 数据表：
  - sbd_cpm.quotation_gene_synthesis 
  - sbd_cpm.pcr_cloning_list 
  - sbd_cpm.point_mutation_list  
  
```bash
# command
docker exec cpm_etl_script python etl_spider_data/etl_admin_quotation_file.py
```

## 清除缓存的数据
- FLOW名称：clean_up_admin_file  

```bash
# command
rm -rf /opt/data/cpm_etl/_temp
```

## 合并数据，发送提醒邮件
- 脚本：cpm_quotation_inform.py
- FLOW名称：cpm_quotation_inform  

```bash
# command
docker exec cpm_etl_script python etl_cpm_data/cpm_quotation_inform.py
```

## 清除缓存的附件
- FLOW名称：clean_up_attachment  

```bash
# command
docker exec cpm_etl_script rm -rf utils/_temp
```

