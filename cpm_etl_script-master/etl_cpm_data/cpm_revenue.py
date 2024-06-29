import pandas as pd
from urllib import parse
from sqlalchemy import create_engine
import sys
import datetime
import os


class CPMRevenue(object):

	def __init__(self, priceDict):
		self.priceDict = priceDict
		self.engine = create_engine(f'mysql+pymysql://sbd_cpm:{parse.quote_plus("cpmUs21!")}@10.13.123.147:3306/sbd_cpm')
		self.order_list = None
		self.order_list_header = None
		self.inqury_list = None
		self.gene_inqury_list = None
		self.clone_inqury_list = None
		self.mutation_inqury_list = None
		self.plasmid_inqury_list = None




	def get_quotation_header(self):
		"""
		2:报价中
		3:已发布
		4:已确认
		:return:
		"""
		sql_query = "SELECT * FROM quotation_header"
		self.order_list_header = pd.read_sql_query(sql_query, self.engine)

	def get_quotation_list(self):
		"""
		2:报价中
		3:已发布
		4:已确认
		:return:
		"""
		sql_query = "SELECT * FROM quotation_list"

		self.order_list = pd.read_sql_query(sql_query, self.engine)
		self.order_list.replace({"quotation_status": {"1": "待报价","2": "报价中", "3": "已发布", "4": "已确认"}}, inplace=True)


	def get_inqury_list(self):

		sql_query = "SELECT * FROM quotation_amount_period"
		self.inqury_list = pd.read_sql_query(sql_query, self.engine)

		self.gene_inqury_list = self.inqury_list[self.inqury_list["type"] == "gene"][["cpm_id", "quotation_code", "SequenceName", "ServicePriority", "type", "IsServicePriority", "GeneLength","IsCodonOptimization"]]
		self.clone_inqury_list = self.inqury_list[self.inqury_list["type"] == "pcr"][["cpm_id", "quotation_code", "SequenceName","ServicePriority", "type"]]
		self.mutation_inqury_list = self.inqury_list[self.inqury_list["type"] == "mt"][["cpm_id", "quotation_code", "SequenceName","ServicePriority","type"]]
		self.plasmid_inqury_list = self.inqury_list[self.inqury_list["type"] == "pre"][["cpm_id", "quotation_code", "SequenceName", "ServicePriority", "type", "PreparationAmount", "EndotoxinLevel"]]

		self.gene_inqury_list = self.gene_inqury_list.dropna(subset=["GeneLength"])



	def update_database(self):
		self.get_quotation_header()
		self.get_quotation_list()
		self.get_inqury_list()

	def gene_price(self, IsServicePriority, GeneLength):
		price = None
		days = None
		if IsServicePriority == "N":
			priceMap = self.priceDict["GeneSynthesis"]["Normal_Gene_Synthesis"]["priceMap"]
			leadTime = self.priceDict["GeneSynthesis"]["Normal_Gene_Synthesis"]["leadTime"]

			if int(GeneLength) <= 400:
				price = priceMap[0]["price"]
			if int(GeneLength) > 400:
				price = priceMap[1]["price"] * int(GeneLength)
			if int(GeneLength) < 3001:
				for lead in leadTime[:-1]:
					if int(GeneLength) in range(lead["intervalDays"][0], lead["intervalDays"][1]):
						if lead["days"]:
							days = lead["days"]
						else:
							days = ["~", "~"]
						break
			if int(GeneLength) >= 3001:
				days = leadTime[-1]["days"]
		if IsServicePriority == "Y":
			priceMap = self.priceDict["GeneSynthesis"]["Accelerated_Gene_Synthesis"]["priceMap"]
			leadTime = self.priceDict["GeneSynthesis"]["Accelerated_Gene_Synthesis"]["leadTime"]
			if int(GeneLength) <= 400:
				price = priceMap[0]["price"]
			if int(GeneLength) > 400:
				price = priceMap[1]["price"] * int(GeneLength)
			if int(GeneLength) < 3001:
				for lead in leadTime[:-1]:
					if int(GeneLength) in range(lead["intervalDays"][0], lead["intervalDays"][1]):
						if lead["days"]:
							days = lead["days"]
						else:
							days = ["~", "~"]
			if int(GeneLength) >= 3001:
				days = leadTime[-1]["days"]
		return int(price), days

	def pcrClone_price(self):
		price = self.priceDict["PCRCloning"]["price"]
		days = self.priceDict["PCRCloning"]["days"]
		return int(price), [str(day) for day in days]


	def pointMutation_price(self):
		price = self.priceDict["PointMutation"]["price"]
		days = self.priceDict["PointMutation"]["days"]
		return int(price), [str(day) for day in days]

	def saturationMutation_price(self):
		price = self.priceDict["Site-saturation Mutagenesis"]["price"]
		days = self.priceDict["Site-saturation Mutagenesis"]["days"]
		return int(price), [str(day) for day in days]

	def plasmid_price(self, amount, endotoxin):
		endotoxinSTD = self.priceDict["PlasmidPrep"]["dataMap"][endotoxin]
		price = self.priceDict["PlasmidPrep"][amount][endotoxinSTD]
		if price == "NA":
			price = 0
		days = self.priceDict["PlasmidPrep"][amount]["days"]

		return int(price), [str(day) for day in days], endotoxinSTD

	def calculate(self, out_put_path):
		self.update_database()
		# 表头
		gene_columns = self.gene_inqury_list.columns.tolist()
		gene_columns.append("Price")
		gene_columns.append("Days")

		# 价格计算
		gene_inqury_list = self.gene_inqury_list.values.tolist()
		for inqury in gene_inqury_list:
			gene_return = self.gene_price(inqury[5], inqury[6])
			inqury.append(gene_return[0])
			inqury.append(gene_return[1])
		# 添加表头
		gene_inqury_list = pd.DataFrame(gene_inqury_list)
		gene_inqury_list.columns = gene_columns


		# 表头
		clone_columns = self.clone_inqury_list.columns.tolist()
		clone_columns.append("Price")
		clone_columns.append("Days")
		# 价格计算
		pcrClone_return = self.pcrClone_price()
		clone_inqury_list = self.clone_inqury_list.values.tolist()
		for inqury in clone_inqury_list:
			inqury.append(pcrClone_return[0])
			inqury.append(pcrClone_return[1])
		# 添加表头
		clone_inqury_list = pd.DataFrame(clone_inqury_list)
		clone_inqury_list.columns = clone_columns


		# 表头
		mutation_columns = self.mutation_inqury_list.columns.tolist()
		mutation_columns.append("Price")
		mutation_columns.append("Days")
		# 价格计算
		pointMutation_return = self.pointMutation_price()
		mutation_inqury_list = self.mutation_inqury_list.values.tolist()
		for inqury in mutation_inqury_list:
			inqury.append(pointMutation_return[0])
			inqury.append(pointMutation_return[1])

		# 添加表头
		mutation_inqury_list = pd.DataFrame(mutation_inqury_list)
		mutation_inqury_list.columns = mutation_columns


		# 表头
		plasmid_columns = self.plasmid_inqury_list.columns.tolist()
		plasmid_columns.append("Price")
		plasmid_columns.append("Days")

		plasmid_inqury_list = self.plasmid_inqury_list.values.tolist()
		for inqury in plasmid_inqury_list:
			plasmid_return = self.plasmid_price(inqury[5], inqury[6])
			inqury.append(plasmid_return[0])
			inqury.append("~".join(plasmid_return[1]))
		# 添加表头
		plasmid_inqury_list = pd.DataFrame(plasmid_inqury_list)
		plasmid_inqury_list.columns = plasmid_columns


		genedf = [self.order_list, self.order_list_header, gene_inqury_list]
		pcrdf = [self.order_list, self.order_list_header, clone_inqury_list]
		mutationdf = [self.order_list, self.order_list_header, mutation_inqury_list]
		pladmiddf = [self.order_list, self.order_list_header, plasmid_inqury_list]

		from functools import reduce
		gene_final = reduce(lambda left, right: pd.merge(left, right, on='cpm_id'), genedf)
		gene_final = gene_final[
			["quotation_code_x", "quotation_status", "wbp_code", "archive_date", "cpm_id", "customer", "customer_contacts",
				"customer_phone", "customer_email", "confirm_time", "service_contacts", "service_phone", "service_email",
				"publish_time", "SequenceName", "ServicePriority", "IsServicePriority", "GeneLength", "IsCodonOptimization", "Price", "Days"]]
		pcr_final = reduce(lambda left, right: pd.merge(left, right, on='cpm_id'), pcrdf)

		pcr_final = pcr_final[
			["quotation_code_x", "quotation_status", "wbp_code", "archive_date", "cpm_id", "customer", "customer_contacts",
				"customer_phone", "customer_email", "confirm_time", "service_contacts", "service_phone", "service_email",
				"publish_time","SequenceName", "ServicePriority", "Price", "Days"]]
		mutation_final = reduce(lambda left, right: pd.merge(left, right, on='cpm_id'), mutationdf)
		mutation_final = mutation_final[
			["quotation_code_x", "quotation_status", "wbp_code", "archive_date", "cpm_id", "customer", "customer_contacts",
				"customer_phone", "customer_email", "confirm_time", "service_contacts", "service_phone", "service_email",
				"publish_time","SequenceName","ServicePriority", "Price", "Days"]]
		pladmid_final = reduce(lambda left, right: pd.merge(left, right, on='cpm_id'), pladmiddf)
		pladmid_final = pladmid_final[
			["quotation_code_x", "quotation_status", "wbp_code", "archive_date", "cpm_id", "customer", "customer_contacts",
				"customer_phone", "customer_email", "confirm_time", "service_contacts", "service_phone", "service_email",
				"publish_time", "SequenceName", "ServicePriority", "PreparationAmount", "EndotoxinLevel", "Price", "Days"]]
		with pd.ExcelWriter(out_put_path) as writer:
			gene_final.to_excel(writer, sheet_name='基因合成')
			pcr_final.to_excel(writer, sheet_name='PCR克隆')
			mutation_final.to_excel(writer, sheet_name='基因突变')
			pladmid_final.to_excel(writer, sheet_name='质粒抽提')


if __name__ == "__main__":
	priceDict = {
		"GeneSynthesis": {
			"threshold": 400,
			"priceUnits": "RMB",
			"Normal_Gene_Synthesis": {
				"units": "bp",
				"priceMap": [{
					"intervalLength": [0, 400],
					"lessOrEqual": True,
					"price": 400,
					"units": "基因"
				}, {
					"intervalLength": [400, "Infinity"],
					"price": 1.02,
					"units": "bp"
				}],
				"leadTime": [{
					"intervalDays": [0, 401],
					"lessOrEqual": True,
					"days": [7, 9]
				}, {
					"intervalDays": [401, 1501],
					"days": [9, 12]
				}, {
					"intervalDays": [1501, 2001],
					"days": [10, 14]
				}, {
					"intervalDays": [2001, 3001],
					"days": [14, 21]
				}, {
					"intervalDays": [3001, "Infinity"],
					"days": [18, 27]
				}]
			},
			"Accelerated_Gene_Synthesis": {
				"units": "bp",
				"priceMap": [{
					"intervalLength": [0, 400],
					"lessOrEqual": True,
					"price": 680,
					"units": "基因"
				}, {
					"intervalLength": [400, "Infinity"],
					"price": 1.7,
					"units": "bp"
				}],
				"leadTime": [{
					"intervalDays": [0, 401],
					"days": [5, 7]
				}, {
					"intervalDays": [401, 1501],
					"days": [7, 10]
				}, {
					"intervalDays": [1501, 2001],
					"days": [9, 12]
				}, {
					"intervalDays": [2001, 3001],
					"days": [10, 14]
				}, {
					"intervalDays": [3001, "Infinity"],
					"days": [14, 18]
				}]
			}
		},
		"PCRCloning": {
			"price": 680,
			"units": "克隆",
			"days": [7]
		},
		"PointMutation": {
			"price": 680,
			"units": "突变",
			"days": [7]
		},
		"Site-saturation Mutagenesis": {
			"price": 10000,
			"units": "个",
			"days": [14, 21]
		},
		"PlasmidPrep": {
			"dataMap": {
				"Don’t control": "noControl",
				"<50EU/µg": "lessThan50",
				"<0.1EU/µg": "lessThan01",
			},
			"10µg": {
				"noControl": 60,
				"lessThan50": "NA",
				"lessThan01": "NA",
				"days": [1, 2],
				"units": ""
			},
			"50µg": {
				"noControl": 400,
				"lessThan50": 480,
				"lessThan01": 560,
				"days": [2, 3],
				"units": ""
			},
			"100µg": {
				"noControl": 650,
				"lessThan50": 780,
				"lessThan01": 910,
				"days": [2, 3],
				"units": ""
			},
			"200µg": {
				"noControl": 800,
				"lessThan50": 960,
				"lessThan01": 1120,
				"days": [2, 3],
				"units": ""
			},
			"500µg": {
				"noControl": 980,
				"lessThan50": 1180,
				"lessThan01": 1380,
				"days": [2, 3],
				"units": ""
			},
			"1mg": {
				"noControl": 1250,
				"lessThan50": 1500,
				"lessThan01": 1750,
				"days": [2, 3],
				"units": ""
			},
			"2mg": {
				"noControl": 1750,
				"lessThan50": 2100,
				"lessThan01": 2450,
				"days": [2, 3],
				"units": ""
			},
			"5mg": {
				"noControl": 2850,
				"lessThan50": 3420,
				"lessThan01": 3990,
				"days": [2, 3],
				"units": ""
			},
			"10mg": {
				"noControl": 4100,
				"lessThan50": 4920,
				"lessThan01": 5740,
				"days": [2, 3],
				"units": ""
			}
		}
	}

	cpmrevenue = CPMRevenue(priceDict=priceDict)
	args = sys.argv
	out_put_dir = args[1] if len(args) > 1 else './'
	now = datetime.datetime.now()
	now_str = now.strftime('%Y%m%d%H%M%S')
	file_name = f'cpm_{now_str}.xlsx'
	out_put_path = os.path.join(out_put_dir, file_name)
	cpmrevenue.calculate(out_put_path)
	print('---DONE---')
