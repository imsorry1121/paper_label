import os
import json
import utility as ut
import codecs
input_path = '../input/'
paper_path = "paper/"
topic_path = "topic/"
output_path = '../output/'
pred_path = "../prediction/"
public_path = "../website/public/"

'''
Statistics
'''

# Description: Calculate type distribution of each journal
# Input: parsed json data: origin.json
# Output: stat_type.csv
# Return:
def stat_type(input_path, output_path):
	cate_papers = dict()
	with open(input_path, "r") as fi:
		cate_papers = json.loads(fi.read())
	type_list = list()
	cate_journal_type_distri = dict()
	with open(output_path, "w") as fo:
		for cate, cate_dict in cate_papers.items():
			cate_journal_type_distri[cate] = dict()
			# fo.write(cate+'\n')
			for journal, articles in sorted(cate_dict.items()):
				cate_journal_type_distri[cate][journal] = dict()
				type_dict = dict()
				# fo.write(journal+'\n')
				for article in articles:
					type_dict[article['type']] = type_dict.get(article['type'], 0)+1
				for type_str, count in sorted(type_dict.items()):
					if type_str not in type_list:
						type_list.append(type_str)
					cate_journal_type_distri[cate][journal][type_str] = count
					# fo.write(","+type_str+','+str(count)+'\n')
			# fo.write('\n')
		type_list = sorted(type_list)
		for type_str in type_list:
			fo.write(","+type_str)
		fo.write("\n")
		for cate, cate_dict in sorted(cate_journal_type_distri.items()):
			for journal, type_distri in sorted(cate_dict.items()):
				fo.write(journal)
				for type_str in type_list:
					fo.write(","+str(type_distri.get(type_str, 0)))
				fo.write("\n")

def stat_label(input_path="../prediction/input/"):
	cates = ["information management","marketing", "transportation", "om&or"]
	data = ut.readJson2Dict(input_path, "data_labeled.json")
	data_labeled = {"information management": {"1":list(), "2": list()}, "marketing": {"1":list(), "2": list()}, "transportation": {"1":list(), "2": list()}, "om&or": {"1":list(), "2": list()}}
	# four cate, two step
	for paper in data:
		if paper["fields"]["is_phased1"]:
			data_labeled[paper["fields"]["category"]]["1"].append(paper)
		elif paper["fields"]["is_phased2"]:
			data_labeled[paper["fields"]["category"]]["2"].append(paper)
		else:
			pass
	print(",label1 vs label2, label1 vs label_final, label_final vs label2")
	for cate in cates:
		# phase 1
		print(cate.upper())
		for i in range(1,3):
			papers = data_labeled[cate][str(i)]
			answers1 = [paper["fields"]["label1"] for paper in papers]
			answers2 = [paper["fields"]["label2"] for paper in papers]
			answers_final = [paper["fields"]["label_final"] for paper in papers]
			print("Phase"+str(i),kappa(answers1, answers2), kappa(answers1, answers_final), kappa(answers2, answers_final))


def stat_user(input_path="../prediction/input/"):

	cates = ["information management","marketing", "transportation", "om&or"]
	data = ut.readJson2Dict(input_path, "data_labeled.json")
	users = ut.readJson2Dict("../website/public/", "data_user1.json")
	data_labeled = {"information management": {"1":list(), "2": list()}, "marketing": {"1":list(), "2": list()}, "transportation": {"1":list(), "2": list()}, "om&or": {"1":list(), "2": list()}}
	results = dict()
	# four cate, two step
	for paper in data:
		if paper["fields"]["is_phased1"]:
			data_labeled[paper["fields"]["category"]]["1"].append(paper)
		elif paper["fields"]["is_phased2"]:
			data_labeled[paper["fields"]["category"]]["2"].append(paper)
		else:
			pass
	with codecs.open("../output/stat_user.txt", "w", encoding="big5") as fo:
		for cate in cates:
			fo.write(cate.upper()+"\n")
			# print(cate.upper())
			for i in range(1,3):
				papers = data_labeled[cate][str(i)]
				time1 = sum([paper["fields"]["time1"] for paper in papers if paper["fields"]["time1"]<1200])/len(papers)
				time2 = sum([paper["fields"]["time2"] for paper in papers if paper["fields"]["time2"]<1200])/len(papers)
				users_cate = [user["fields"]["name"] for user in users if user["fields"]["category"]==cate]
				fo.write(" ".join(["Phase"+str(i), users_cate[0], str(time1), users_cate[1], str(time2)])+"\n")
				# print("Phase"+str(i), users_cate[0], time1, users_cate[1], time2)



def kappa(answers1, answers2):
	ratios1 = dict()
	ratios2 = dict()
	total = len(answers1)
	po = 0
	for index, answer1 in enumerate(answers1):
		answer2 = answers2[index]
		if answer1 == answer2:
			po+=1
		ratios1[answer1] =  ratios1.get(answer1, 0)+1
		ratios2[answer2] =  ratios2.get(answer2, 0)+1
	keys = list(set(ratios1.keys()).union(set(ratios2.keys())))
	po /= total
	pe = 0
	for key in keys:
		pe += (ratios1.get(key,0)*ratios2.get(key,0)/total/total)
	k = (po-pe)/(1-pe)
	return k

def stat_others(input_path="../prediction/input/"):
	cates = ["information management","marketing", "transportation", "om&or"]
	data = ut.readJson2Dict(input_path, "data_labeled.json")
	topics = ["Others but relevant to IM", "Others but relevant to Marketing", "Others but relevant to OM", "Others but relevant to Transportation", "Not relevant", "Other Methods", "Relevant to IM", "Relevant to Transportation", "Relevant to Marketing", "Not Relevant to All Fields"]
	paper_cate = {"information management": dict(),"marketing": dict(), "transportation": dict(), "om&or": dict()}
	for paper in data:
		label = paper["fields"]["label_final"].strip()
		tmp = label.lower()
		if "relevant" in tmp or "relevent" in tmp:
		# if label in topics:
			cate = paper["fields"]["category"]
			tmp = paper_cate[cate].get(label, list())
			tmp.append(paper)
			paper_cate[cate][label] = tmp
	for cate in cates:
		fo = open(cate+".csv", "w")
		fields = ["title","author","journal","volume","number","pages","year","month","keyword","keyword-plus","abstract"]
		fo.write(","+",".join(fields)+"\n")
		cate_topics = paper_cate[cate]
		for cate_topic, papers in cate_topics.items():
			fo.write(cate_topic)
			for paper in papers:
				for field in fields:
					fo.write(",\""+paper["fields"].get(field,"")+"\"")
				fo.write("\n")










if __name__ == "__main__":
	# stat_label()
	# stat_user()
	stat_others()





