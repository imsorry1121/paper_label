import os
import json
import utility as ut
import codecs
import csv
input_path = '../input/'
paper_path = "paper/"
topic_path = "topic/"
output_path = '../output/'
pred_path = "../prediction/"
result_path = "../result/"
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

def stat_label2(input_path="../result/"):
	cates = ["information management","marketing", "transportation", "om&or"]
	data = ut.readJson2Dict(input_path, "data_final.json")
	data_labeled = {"information management": list(), "marketing": list(), "transportation": list(), "om&or": list()}
	for paper in data:
		if paper["fields"]["phased3"]==3:
			data_labeled[paper["fields"]["category"]].append(paper)
	for cate in cates:
		print(cate.upper())
		papers = data_labeled[cate]
		jaccards = list()
		aligns = list()
		for paper in papers:
			s1 = set(paper["fields"]["label3"].split(";"))
			s2 = set(paper["fields"]["label4"].split(";"))
			jaccards.append(jaccard(s1,s2))
			aligns.append(align_ratio(s1,s2,3))
		print("Jaccards:", sum(jaccards)/len(jaccards))
		print("Alignment Ratio:", sum(aligns)/len(aligns))


def stat_user2(input_path="../result/"):
	cates = ["information management","marketing", "transportation", "om&or"]
	data = ut.readJson2Dict(input_path, "data_final.json")
	users = ut.readJson2Dict("../website/public/", "data_user1.json")
	data_labeled = {"information management": list(), "marketing": list(), "transportation": list(), "om&or": list()}
	results = dict()
	for paper in data:
		data_labeled[paper["fields"]["category"]].append(paper)
	with codecs.open("../output/stat_user2.txt", "w", encoding="big5") as fo:
		for cate in cates:
			fo.write(cate.upper()+"\n")
			papers = data_labeled[cate]
			print(len(papers))
			time3s = [paper["fields"]["time3"] for paper in papers if paper["fields"]["time3"]<1200 and paper["fields"]["time3"]>0]
			time4s = [paper["fields"]["time4"] for paper in papers if paper["fields"]["time4"]<1200 and paper["fields"]["time4"]>0]
			avg_time3 = sum(time3s)/len(time3s) 
			avg_time4 = sum(time4s)/len(time4s)
			users_cate = [user["fields"]["name"] for user in users if user["fields"]["category"]==cate]
			fo.write(" ".join([users_cate[0], str(avg_time3), users_cate[1], str(avg_time4)])+"\n")
			

def jaccard(s1, s2):
	return len(s1.intersection(s2))/len(s1.union(s2))

def align_ratio(s1, s2, n):
	count = 0
	if len(s1)<n and len(s2)<n:
		count+= (2*n-len(s1)-len(s2))
	count += len(s1.union(s2))
	return count/(2*n)

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
		fo = open("../problem/"+cate+".csv", "w")
		fields = ["title","author","journal","volume","number","pages","year","month","keyword","keyword-plus","abstract"]
		fo.write(","+",".join(fields)+"\n")
		cate_topics = paper_cate[cate]
		for cate_topic, papers in cate_topics.items():
			fo.write(cate_topic)
			for paper in papers:
				for field in fields:
					fo.write(",\""+paper["fields"].get(field,"")+"\"")
				fo.write("\n")

def stat_journal(input_path="../result/", fname="data_final.json"):
	fo = open("../output/stat_journal.csv", "w")
	papers = ut.readJson2Dict(input_path, fname)
	print(len(papers))
	paper_cate_journal = dict()
	for p in papers:
		cate = p["fields"]["category"].upper()
		journal = p["fields"]["journal"]
		vol = p["fields"]["volume"]
		no = p["fields"]["number"].replace(",","")
		if paper_cate_journal.get(cate, 0) == 0:
			paper_cate_journal[cate] = dict()
		if paper_cate_journal[cate].get(journal, 0) == 0:
			paper_cate_journal[cate][journal] = dict()
		if paper_cate_journal[cate][journal].get(vol, 0) == 0:
			paper_cate_journal[cate][journal][vol] = dict()
		if paper_cate_journal[cate][journal][vol].get(no, 0) == 0:
			paper_cate_journal[cate][journal][vol][no] = 0
		paper_cate_journal[cate][journal][vol][no]+=1
	len(paper_cate_journal)
	for cate, journals in paper_cate_journal.items():
		for j, vols in sorted(journals.items()):
			for v, nos in sorted(vols.items()):
				for no, count in sorted(nos.items()):
					fo.write(cate+","+j+","+v+","+no+","+str(count)+"\n")
	fo.close()

# 1. 看答案個數的分佈比例
def stat_label_distri(input_path="../result/"):
	cates = ["information management","marketing", "transportation", "om&or"]
	data = ut.readJson2Dict(input_path, "data_final.json")
	data_labeled = {"information management": list(), "marketing": list(), "transportation": list(), "om&or": list()}

	for paper in data:
		if paper["fields"]["phased3"]==3:
			s = set(paper["fields"]["label3"].split(";")).union(set(paper["fields"]["label4"].split(";")))
		elif paper["fields"]["phased3"]==2:
			s = set(paper["fields"]["label4"].split(";"))
		else:
			s =set(paper["fields"]["label3"].split(";"))
		data_labeled[paper["fields"]["category"]].append(s)
	for cate in cates:
		print(cate.upper())
		label_len_distri = dict()
		for s in data_labeled[cate]:
			label_len_distri[len(s)] = label_len_distri.get(len(s),0) +1
		for k, v in sorted(label_len_distri.items()):
			print(k, v/len(data_labeled[cate]))

def stat_other_label(input_path="../result/"):
	mapping = {'information management': 'Others but relevant to IM','marketing':'Others but relevant to Marketing', 'transportation':'Others but relevant to Transportation', 'om&or':'Others but relevant to OM&OR'}
	data = ut.readJson2Dict(input_path, "data_final.json")
	data_labeled = {"information management": list(), "marketing": list(), "transportation": list(), "om&or": list()}

	# read data
	for paper in data:
		cate = paper["fields"]["category"]
		if paper["fields"]["phased3"]==3:
			s = set(paper["fields"]["label3"].split(";")).union(set(paper["fields"]["label4"].split(";")))
		elif paper["fields"]["phased3"]==2:
			s = set(paper["fields"]["label4"].split(";"))
		else:
			s =set(paper["fields"]["label3"].split(";"))
		if mapping[cate] in s:
			data_labeled[cate].append(paper)
	# output data
	cols = ['isi', 'title', 'author', 'journal', 'year', 'month', 'volume', 'number', 'pages', 'keyword', 'keywords_plus','web_of_science_categories', 'abstract']
	for cate, papers in data_labeled.items():
		output_paper("../output/stat_label_others_"+cate+".csv", papers)
	

# 2. 看每個年份前十高的標籤組合
def stat_top_label(input_path="../result/"):
	fo = codecs.open("../output/stat_top_label.csv", "w", encoding="big5")
	w = csv.writer(fo)
	cates = ["information management","marketing", "transportation", "om&or"]
	data = ut.readJson2Dict(input_path, "data_final.json")
	data_labeled = {"information management": dict(), "marketing": dict(), "transportation": dict(), "om&or": dict()}
	for paper in data:
		year = paper["fields"]["year"]
		cate = paper["fields"]["category"]
		if paper["fields"]["phased3"]==3:
			s = set(paper["fields"]["label3"].split(";")).union(set(paper["fields"]["label4"].split(";")))
		elif paper["fields"]["phased3"]==2:
			s = set(paper["fields"]["label4"].split(";"))
		else:
			s =set(paper["fields"]["label3"].split(";"))
		combinations = get_combination(s)
		# s = ";".join(sorted(list(s)))
		if data_labeled[cate].get(year, 0)==0:
			data_labeled[cate][year] = dict()
		for c in combinations:
			data_labeled[cate][year][c] = data_labeled[cate][year].get(c,0) + 1
	for cate in cates:
		w.writerow([cate.upper()])
		for year, sets in sorted(data_labeled[cate].items()):
			topn = sorted([(count, s) for s, count in sets.items()], reverse=True)[:10]
			# fo.write(str(year)+","+",".join([s for count, s in topn])+"\n")
			w.writerow([year]+[s for count, s in topn])
	fo.close()

def output_err_data():
	data = ut.readJson2Dict(result_path, "data_final.json")
	papers_428 = list()
	# 2. excel row 428
	for p in data:
		if p["fields"]["journal"] == "JOURNAL OF MANAGEMENT INFORMATION SYSTEMS" and p["fields"]["volume"]=="31" and p["fields"]["number"]=="4":
		# if p["fields"]["journal"] == "JOURNAL OF MANAGEMENT INFORMATION SYSTEMS":
			print(p["fields"]["title"])
			papers_428.append(p)
	output_paper("../output/stat_error_428.csv", papers_428)
	# 3. excel row 657
	papers_657 = list()
	for p in data:
		if p["fields"]["journal"] == "TRANSPORTATION RESEARCH PART C-EMERGING TECHNOLOGIES" and p["fields"]["volume"]=="47":
		# if p["fields"]["journal"] == "JOURNAL OF MANAGEMENT INFORMATION SYSTEMS":
			print(p["fields"]["title"])
			papers_657.append(p)
	output_paper("../output/stat_error_657.csv", papers_657)
	# for p in data:

'''
Helper function
'''
def output_paper(fname, papers):
	fo = codecs.open(fname, "w", encoding="big5")
	w = csv.writer(fo)
	cols = ["isi","title","author","journal","volume","number","pages","year","month","keyword","keyword-plus","abstract"]
	w.writerow(cols)
	for p in papers:
		w.writerow([p["fields"].get(col,"") for col in cols])
	fo.close()



def get_combination(s):
	labels = sorted(list(s))
	print(labels)
	results = list()
	if len(labels)<=2:
		results = [";".join(labels)]
	else:
		for i in range(len(labels)):
			for j in range(i+1, len(labels)):
				results.append(labels[i]+";"+labels[j])
	return results


if __name__ == "__main__":
	# stat_label()
	# stat_user()
	# stat_others()
	# stat_user2()
	# stat_label2()
	# stat_journal()
	# stat_label_distri()
	# stat_top_label()
	# stat_other_label()
	output_err_data()





