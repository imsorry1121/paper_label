import bibtexparser
import os 
import json
import random
import re
import codecs
import math
# marketing science
fields = ['ID', 'author', 'title', 'journal', 'year', 'volumn', 'number', 'pages', 'month', \
'volume', 'abstract', 'type', 'keyword', 'keywords-plus', 'web-of-science-categories']
input_path = '../input/'
paper_path = "paper/"
paper_new_path = "paper_new/"
topic_path = "topic/"
output_path = '../output/'
public_path = "../website/public/"
parsed_file = "parsed.json"

'''
Data preprocess
'''
'''
Paper
'''
# Description:
# Input:
# Output:
# Return:
def preprocess_paper():
	cate_papers = dict()
	for path, folders, filenames in os.walk(input_path+paper_path):
		papers = list()
		category = str()
		journal = str()
		for filename in filenames:
			if '.bib' in filename:
				category = path.split("/")[-2]
				journal = path.split("/")[-1]
				# print(os.path.join(path, filename))
				papers += parse_paper(os.path.join(path, filename))
		if len(papers) > 0: 
			if cate_papers.get(category, 0) == 0:
				cate_papers[category] = dict()
			cate_papers[category][journal] = papers
			# print(category+","+journal+","+str(len(papers)))
	# papers_add = parse_paper_new("../input/paper/OM&OR/Production and Operations Management/Production and Operations Management(2).bib")
	# cate_papers["OM&OR"]["Production and Operations Management"]+=papers_add

	write_json(output_path+parsed_file, cate_papers)

# Description: preprocess new download paper
def preprocess_paper2():
	mapping = {"IM": "information management", "Marketing":"marketing", "OM&OR":"om&or", "Transportation": "transportation"}
	cate_papers = dict()
	for path, folders, fnames in os.walk(input_path+paper_new_path):
		papers = list()
		for fname in fnames:
			if '.bib' in fname:
				category = mapping[path.split("/")[-1].split("-")[0]]
				journal = path.split("/")[-1].split("-")[1]
				papers += parse_paper(os.path.join(path, fname))
		if len(papers) > 0: 
			if cate_papers.get(category, 0) == 0:
				cate_papers[category] = dict()
			cate_papers[category][journal] = papers
	write_json(output_path+"parsed2.json", cate_papers)


def preprocess_editorial():
	for path, folders, fnames in os.walk(input_path+paper_path+"Information Management/"):
		papers = list()
		for fname in fnames:
			if '.bib' in fname:
				# journal = path.split("/")[-1].split("-")[1]
				papers += parse_editorial_paper(os.path.join(path, fname))
	write_json(output_path+"parsed_edit_im.json", papers)

def parse_editorial_paper(input_file="../input/Marketing/Marketing Science/Marketing Science(1).bib"):
	papers_all = list()
	paper_type = "Editorial Material"
	with open(input_file, "r") as fi:
		papers = bibtexparser.loads(fi.read())
	# one bib one article
	for paper in papers.entries:
		if paper["type"] != paper_type:
			continue
		if paper.get("abstract","") == "":
			title = remove_reduct_symbol(paper["title"])
		paper_info = dict()
		for key, value in paper.items():
			if key in fields:
				paper_info[key] = remove_reduct_symbol(value)
		papers_all.append(paper_info)
	return papers_all



# def parse_paper_new2(input_path="../input/paper_new/")

def parse_paper_new(input_file="../input/Marketing/Marketing Science/Marketing Science(1).bib"):
	papers_all = list()
	papers_add2 = parse_paper_add(input_path+"paper_add2")
	with open(input_file, "r") as fi:
		papers = bibtexparser.loads(fi.read())
	# one bib one article
	for paper in papers.entries:
		if paper["type"] != "Article":
			continue
		if paper.get("abstract","") == "":
			title = remove_reduct_symbol(paper["title"])
			if papers_add2.get(title,"") != "":
				paper["abstract"] = papers_add2[title]
			else:
				continue
			paper_info = dict()
			for key, value in paper.items():
				if key in fields:
					paper_info[key] = remove_reduct_symbol(value)
			papers_all.append(paper_info)
	return papers_all

def parse_paper(input_file="../input/Marketing/Marketing Science/Marketing Science(1).bib"):
	papers_all = list()
	papers_add1 = parse_paper_add(input_path+"paper_add")
	with open(input_file, "r") as fi:
		papers = bibtexparser.loads(fi.read())
	# one bib one article
	for paper in papers.entries:
		if paper["type"] != "Article":
			continue
		if paper.get("abstract","") == "":
			title = remove_reduct_symbol(paper["title"])
			if papers_add1.get(title,"") != "":
				paper["abstract"] = papers_add1[title]
			else:
				continue
		paper_info = dict()
		for key, value in paper.items():
			if key in fields:
				paper_info[key] = remove_reduct_symbol(value)
		papers_all.append(paper_info)
	return papers_all

def parse_paper_add(filename):
	papers_abstract = dict()
	with open(filename, "r") as fi:
		for line in fi:
			tmp = line.split("\t")
			title = tmp[0].strip()
			abstract = tmp[1].strip()
			papers_abstract[title] = abstract
	return papers_abstract


def remove_reduct_symbol(sentence):
	return sentence.replace("\\","").replace("``", "").replace("{''}","").replace("\n", " ").replace("{[}", "[").replace("`","'")

'''
Topic
'''
def preprocess_topic():
	parse_topic_information()
	parse_topic_transportation()
	parse_topic_om()
	parse_topic_marketing()

def parse_topic_information():
	text_origin = str()
	result = list()
	with open(input_path+topic_path+"im", "r") as fi:
		text_origin = fi.read()
	categories = text_origin.split("\n\n")
	for category in categories:
		texts = category.split("\n")
		cate_title = texts[0].strip()
		cate_topic = list()
		for i in range(1, len(texts), 2):
			title = texts[i].split("	")[1].strip()
			desc = texts[i+1].strip()
			cate_topic.append({"title": title, "desc": desc})
		result.append({"title": cate_title, "topics": cate_topic})
	# result.append(parse_relevant("transportation"))
	result = result + parse_topic_append("IM")
	write_json(public_path+"topic_im.json", result)

def parse_topic_transportation():
	text_origin = str()
	result = list()
	with open(input_path+topic_path+"transportation_new", "r") as fi:
		text_origin = fi.read()
	categories = text_origin.split("\n\n")
	for category in categories:
		texts = category.split("\n")
		cate_title = texts[0].split("	")[1].split("(")[0]
		cate_topic = list()
		for i in range(1, len(texts), 2):
			titles, subs = get_multiple_brackets(texts[i].strip().split("	")[1], "、")
			desc = texts[i+1].strip()
			cate_topic.append({"title": "/".join(titles), "sub": ";".join(subs), "desc": desc})
		result.append({"title": cate_title, "topics": cate_topic})
	# result.append(parse_relevant("transportation"))
	result = result + parse_topic_append("Transportation")
	write_json(public_path+"topic_transportation.json", result)

def parse_topic_marketing():
	text_origin = str()
	result = list()
	with open(input_path+topic_path+"marketing_new", "r") as fi:
		text_origin = fi.read()
	categories = text_origin.split("\n\n")
	for category in categories:
		texts = category.split("\n")
		cate_title, cate_sub = get_brackets(texts[0].strip())
		cate_title = cate_title.replace("\t", "")
		cate_desc = texts[1].strip()
		cate_topic = list()
		for text in texts[2:]:
			title, sub = get_brackets(text.strip().replace("\t", ""))
			cate_topic.append({"title": title.strip(), "sub": sub})
		result.append({"title": cate_title, "sub": cate_sub, "desc": cate_desc, "topics": cate_topic})
	# result.append(parse_relevant("marketing"))
	result = result + parse_topic_append("Marketing")
	write_json(public_path+"topic_marketing.json", result)

def parse_topic_om():
	text_origin = str()
	result = list()
	with open(input_path+topic_path+"om_new", "r") as fi:
		text_origin = fi.read()
	categories = text_origin.split("\n\n")
	for category in categories:
		texts = category.split("\n")
		cate_title = texts[0]
		cate_topic = list()
		for text in texts[1:]:
			title, sub = get_brackets(text)
			cate_topic.append({"title": title.strip(), "sub": sub})
		result.append({"title": cate_title, "topics": cate_topic})
	# result.append(parse_relevant("OM&OR"))
	result = result + parse_topic_append("OM&OR")
	write_json(public_path+"topic_om.json", result)

def parse_relevant(cate):
	result = {"title": "Not Relevant", "topics":["Relevant to IM", "Relevant to Transportation", "Relevant to OM&OR", "Relevant to Marketing"]}
	for topic in result["topics"]:
		if cate.lower() in topic.lower():
			result["topics"].remove(topic)
	return result

def parse_topic_append(cate):
	result = list()
	other = {"title": "Others", "topics": [{"title": "Others but relevant to "+cate}]}
	not_relevant = {"title": "Not relevant", "topics": [{"title": "Not relevant"}]}
	result.append(other)
	result.append(not_relevant)
	return result


'''
DB preprocess
'''


def build_db_data():
	# build_db_user()
	build_db_paper()

# revise the user account and pwd
def build_db_user():
	# data = read_parsed_data()
	data = dict()
	instances = list()
	with open(input_path+"user", "r") as fi:
		cates = fi.read().split("\n\n")
	for cate in cates:
		texts = cate.split("\n")
		title = texts[0].strip()
		for i in range(2):
			name = texts[1+i*2].strip()
			account = texts[2+i*2].strip()
			pwd = create_pwd(4)
			instance = dict()
			instance["account"] = account
			instance["pwd"] = pwd
			instance["name"] = name
			instance["category"] = title
			instance["index"] = str(i+1)
			instances.append(instance)
	build_db_format("user.user", instances, public_path+"data_user.json")

def build_db_paper(threshold=200, ratio=0.1):
	data = read_parsed_data()
	cate_papers = dict()
	instances = list()
	for category, cate_dict in sorted(data.items()):
		# concate papers by sorting journal 
		for journal, papers in sorted(cate_dict.items()):
			for paper in papers:
				paper["category"] = category.lower()
				paper["web_of_science_categories"] = paper.get("web-of-science-categories", "")
				paper.pop("web-of-science-categories")
				paper["isi"] = paper.get("ID", "")
				paper.pop("ID")
				# capitaliza?
				paper["keywords_plus"] = ";".join([keyword.strip().title() for keyword in paper.get("keywords-plus", "").split(";")]) 
				paper["keyword"] = ";".join([keyword.strip().title() for keyword in paper.get("keyword", "").split(";")]) 
				# paper["label1"] = ""
				# paper["label2"] = ""
				# paper["prediction"] = ""
				if paper["keywords_plus"] != "":
					paper.pop("keywords-plus")
			cate_papers[category] = cate_papers.get(category, list())+papers
	for category, papers in sorted(cate_papers.items()):
		number = max(threshold, int(len(papers)*0.1))
		samples = get_samples(number, len(papers))
		# samples = random.sample(range(len(papers)), number)
		for index, sample in enumerate(samples):
			if index%2 == 0:
				papers[sample]["is_phased1"] = True	
			else:
				papers[sample]["is_phased2"] = True
		instances += papers
	build_db_format("paper.paper", instances, public_path+"data_paper.json")



def add_db_paper():
	data_new = read_json(output_path+"parsed2.json")
	data_exist = read_json(input_path+"data_final.json")
	isis = [paper["fields"]["isi"] for paper in data_exist]
	instances = list()
	cate_papers = dict()
	# revise label_final
	# revise volume
	for p in data_exist:
		if p["fields"]["label3"] == p["fields"]["label4"]:
			p["fields"]["label_final"] = p["fields"]["label3"]
			print(p["pk"])
		if p["fields"]["journal"] == "JOURNAL OF MANAGEMENT INFORMATION SYSTEMS" and p["fields"]["volume"]=="31" and p["fields"]["number"]=="4":
			print(p["fields"]["year"], p["fields"]["journal"])
			p["fields"]["volume"]="32"
	# parse new papers
	for category, cate_dict in sorted(data_new.items()):
		for j, papers in sorted(cate_dict.items()):
			papers_new = list()
			for paper in papers:
				if paper["ID"] in isis:
					print(paper["title"])
					continue
				paper["category"] = category.lower()
				paper["web_of_science_categories"] = paper.get("web-of-science-categories", "")
				paper.pop("web-of-science-categories")
				paper["isi"] = paper.get("ID", "")
				paper.pop("ID")
				paper["keywords_plus"] = ";".join([keyword.strip().title() for keyword in paper.get("keywords-plus", "").split(";")]) 
				if paper["keywords_plus"] != "":
					paper.pop("keywords-plus")
				paper["keyword"] = ";".join([keyword.strip().title() for keyword in paper.get("keyword", "").split(";")]) 
				# paper["label1"] = ""
				# paper["label2"] = ""
				paper["prediction"] = ""
				paper["time3"] = 0
				paper["time4"] = 0
				paper["label3"] = ""
				paper["label4"] = ""
				papers_new.append(paper)
			cate_papers[category] = cate_papers.get(category, list())+papers_new
	for category, papers in sorted(cate_papers.items()):
		print(category, len(papers))
		for index, p in enumerate(papers):
			papers[index]["phased3"] = index%2+1
		instances += papers
	for index, instance in enumerate(instances):
		row = dict()
		row["fields"] = instance
		row["model"] = "paper.paper"
		row["pk"] = index+1+7405
		data_exist.append(row)
	write_json(public_path+"data_final2.json", data_exist)



def build_db_format(model, instances, path):
	rows = list()
	for index, instance in enumerate(instances):
		row = dict()
		row["fields"] = instance
		row["model"] = model
		row["pk"] = index+1
		rows.append(row)
	write_json(path, rows)



''' 
IO
'''

def read_json(path):
	data = dict()
	with open(path, "r") as fi:
		data = json.loads(fi.read())
	return data

def write_json(path, data):
	with codecs.open(path, "w", encoding="utf8") as fo:
		fo.write(json.dumps(data, indent=4, ensure_ascii=False))

def read_parsed_data():
	data = read_json(output_path+parsed_file)
	return data



'''
Others
'''

def get_multiple_brackets(text, mark):
	items = text.split(mark)
	titles = list()
	subs = list()
	for item in items:
		title, sub = get_brackets(item)
		titles.append(title)
		subs.append(sub)
	return titles, subs


def get_brackets(text):
	result = re.search(r'(.+)\((.+)\)', text)
	if result == None:
		return text, ""
	else:
		return result.group(1).strip(), result.group(2).strip()

def get_samples(k, total):
	a = total/k
	b = random.random() * a
	numbers = list()
	for i in range(k):
		numbers.append(math.floor(a*i+b))
	return numbers

def create_pwd(length):
	alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	pwd = ""
	for i in range(length):
		index = random.randrange(len(alphabet))
		pwd= pwd + alphabet[index]
	return pwd


# def save(output_path, articles ):
# 	for article in articles:
# 		with open(os.path.join, "w") as fo:
# 			fo.write(json.dumps(article, indent=4))

if __name__ == "__main__":
	# preprocess_topic()
	# preprocess_paper()	
	# preprocess_paper2()
	# build_db_data()
	# add_db_paper()
	# parse_topic_information()
	# parse_topic_marketing()
	# parse_topic_transportation()

	# preprocess_editorial()

