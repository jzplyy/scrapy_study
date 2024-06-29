# CPM爬虫
> 这是CPM报价单的一系列爬虫脚本，任务通过[Azkaban 任务调度平台](http://10.13.123.147:8081/) 调度  
> 数据库配置在：`./cpm_spider/settings.py`  
> Azkaban workflow配置在：`./cpm_work_flow`  
> <b>FLOW名称</b>代表在 Azkaban workflow 中的名称

## 注意事项
- 登录有效时长是30分钟，需要在30分钟内完成数据爬取
- 如果账号密码修改，需要在数据库的`spider.account`表中更新 
- 脚本main方法的`CONCURRENT_REQUESTS`参数代表异步并发数，该参数在请求队列量大或`DOWNLOAD_DELAY`=0的时候才会起作用
- 脚本main方法的`DOWNLOAD_DELAY`参数代表每个请求之间的间隔（秒），想要加快爬取速度就把这个参数改小

## 部署信息
- 部署机器：10.13.123.147 
- docker容器：cpm_spider
- 部署路径：/opt/projects/cpm_spider/

## 本地部署
```bash
pip install -r requirements.txt

cd ./scrapyg
python setup.py install
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

## 登录(使用账号登录获取Token)
- 脚本：cpm_login.py
- FLOW名称：login
- 数据表：spider.cpm_login
- <b>注意</b>：如果账号密码修改，需要在`spider.account`表中更新  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_login.py
```

## 报价单 - 列表页
- 脚本：cpm_quotation_list.py
- FLOW名称：quotation_list
- 数据表：spider.cpm_quotation_list  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_quotation_list.py
```

## 管理后台 - 观数台填报 - 任务管理 - 任务监控
- 脚本：cpm_admin_quotation_file.py
- FLOW名称：cpm_admin_quotation_file
- 数据表：spider.cpm_admin_quotation_file  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_admin_quotation_file.py
```

## 报价单 - 首页
- 脚本：cpm_quotation_header.py
- FLOW名称：quotation_header
- 数据表：spider.cpm_quotation_header  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_quotation_header.py
```

## 报价单 - 合同金额和周期
- 脚本：cpm_quotation_amount_period.py
- FLOW名称：quotation_amount_period
- 数据表：spider.cpm_quotation_amount_period  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_quotation_amount_period.py
```

## 报价单 - 点突变 - 序列信息
- 脚本：cpm_point_mutation_sequence.py
- FLOW名称：cpm_point_mutation_sequence
- 数据表：spider.cpm_point_mutation_sequence  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_point_mutation_sequence.py
```

## 报价单 - 点突变 - 列表数据
- 脚本：cpm_point_mutation_list.py
- FLOW名称：cpm_point_mutation_list
- 数据表：spider.cpm_point_mutation_list  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_point_mutation_sequence.py
```

## 报价单 - 质粒制备 - 序列信息
- 脚本：cpm_plasmid_preparation_sequence.py
- FLOW名称：cpm_plasmid_preparation_sequence
- 数据表：spider.cpm_plasmid_preparation_sequence  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_plasmid_preparation_sequence.py
```

## 报价单 - 质粒制备 - 列表数据
- 脚本：cpm_plasmid_preparation_list.py
- FLOW名称：cpm_plasmid_preparation_list
- 数据表：spider.cpm_plasmid_preparation_list  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_plasmid_preparation_list.py
```

## 报价单 - PCR克隆 - 序列信息
- 脚本：cpm_pcr_cloning_sequence.py
- FLOW名称：cpm_pcr_cloning_sequence
- 数据表：spider.cpm_pcr_cloning_sequence  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_pcr_cloning_sequence.py
```

## 报价单 - PCR克隆 - 列表数据
- 脚本：cpm_pcr_cloning_list.py
- FLOW名称：cpm_pcr_cloning_list
- 数据表：spider.cpm_pcr_cloning_list  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_pcr_cloning_list.py
```

## 报价单 - 基因合成
- 脚本：cpm_quotation_gene_synthesis.py
- FLOW名称：quotation_gene_synthesis
- 数据表：spider.cpm_quotation_gene_synthesis  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_quotation_gene_synthesis.py
```

## 报价单 - 基因合成 - 列表数据
- 脚本：cpm_quotation_gene_synthesis_part2.py
- FLOW名称：quotation_gene_synthesis_part2
- 数据表：spider.cpm_quotation_gene_synthesis_part2  

```bash
# command
docker exec cpm_spider python cpm_spider/spiders/cpm_quotation_gene_synthesis_part2.py
```

## 转移爬虫临时文件
- FLOW名称：mv_spider_temp_file  

```bash
# command
mv /opt/projects/cpm_spider/files/_temp /opt/data/cpm_etl/_temp
```







