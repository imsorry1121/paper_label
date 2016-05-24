import utility as ut
import string
import json
import csv

'''
IO
'''
output_path="../result/"

def output_data(input_path ="../result/", output_path="../result/"):
	data = ut.readJson2Dict(input_path, "data_final.json")
	cates = ["information management","marketing", "transportation", "om&or"]
	paper_cate = {"information management": list(), "marketing": list(), "transportation": list(), "om&or": list()}
	output_topics()
	for paper in data:
		paper_cate[paper["fields"]["category"]].append(paper)
	for cate in cates:
		papers = paper_cate[cate]
		# output_article(papers, output_path, cate)
		output_label(papers, output_path, cate)



def output_article(papers, output_path, cate):
	fields = ["title","author","journal","volume","number","pages","year","month","keyword","keyword-plus","abstract"]
	fo = open(output_path+"papers_"+cate+".csv", "w")
	fo.write("index,"+",".join(fields)+"\n")
	for index, paper in enumerate(papers):
		fo.write(str(index+1))
		for field in fields:
			fo.write(",\""+paper["fields"].get(field,"")+"\"")
		fo.write("\n")
	fo.close()

def output_edit_im():
	data = ut.readJson2Dict("../output/", "parsed_edit_im.json")
	fields = ["title","author","journal","volume","number","pages","year","month","keyword","keyword-plus","abstract"]
	fo = open(output_path+"papers_im_editorial"+".csv", "w")
	fo.write("index,"+",".join(fields)+"\n")
	for index, paper in enumerate(data):
		fo.write(str(index+1))
		for field in fields:
			fo.write(",\""+paper.get(field,"")+"\"")
		fo.write("\n")
	fo.close()

def output_label(papers, output_path, cate):
	mapping_cate = read_mapping()
	mapping = mapping_cate[cate]
	labels_all = sorted(mapping.values(), key=lambda x:int(x[1:]))
	labels_all = sorted(labels_all, key=lambda x:x[0])
	filename = "label_"+cate+".csv"
	f = open(output_path+filename, "w")
	f.write("Index,"+",".join(labels_all)+",Coder\n")
	for index, paper in enumerate(papers):
		choose = paper["fields"]["phased3"]
		labels = list()
		if choose==1:
			labels = paper["fields"]["label3"].split(";")
		elif choose==2:
			labels = paper["fields"]["label4"].split(";")
		else:
			labels = list(set(paper["fields"]["label3"].split(";") + paper["fields"]["label4"].split(";")))
		result = ["0"]*(len(labels_all)+2)
		result[0] = str(index+1)
		result[-1] = str(choose)
		for label in labels:
			result[labels_all.index(mapping.get(label))+1] = "1"
		f.write(",".join(result)+"\n")



def output_topics():
	cates = ["information management","marketing", "transportation", "om&or"]
	alpha = string.ascii_uppercase
	topics = read_topics()
	for cate in cates:
		results = list()
		topics_cate = topics[cate]
		for i, sub_cate in enumerate(topics_cate):
			for j, sub_topic in enumerate(sub_cate["topics"]):
				result = ["\""+alpha[i]+str(j+1)+"\"", "\""+sub_topic["title"]+"\""] 
				results.append(result)
		ut.writeList2CommaLine(output_path, "mapping_"+cate+".csv", results)


def read_mapping():
	cates = ["information management","marketing", "transportation", "om&or"]
	mapping_cate = dict()
	for cate in cates:
		filename = "mapping_"+cate+".csv"
		results = readCsvList(output_path, filename)
		mapping = {r[1]:r[0] for r in results}
		mapping_cate[cate] = mapping
	return mapping_cate

def read_topics():
	om_special_topics = [{"title": "Not relevant", "topics": [{"title":"Relevant to IM"}, {"title":"Relevant to Transportation"}, {"title":"Relevant to Marketing"}, {"title":"Not Relevant to All Fields"}]}]
	im = read_json("../website/public/topic_im.json")
	om = read_json("../website/public/topic_om.json")
	transportation = read_json("../website/public/topic_transportation.json")
	marketing = read_json("../website/public/topic_marketing.json")
	topics = {"information management": im, "marketing": marketing, "om&or": om, "transportation": transportation}
	topics["om&or"] += om_special_topics
	return topics

def read_json(filename):
	with open(filename, "r") as fo:
		result = json.loads(fo.read())
	return result

def readCsvList(path, filename):
	results = list()
	with open(path+filename, "r") as fc:
		reader = csv.reader(fc, delimiter=",")
		for row in reader:
			results.append(row)
	return results


if __name__ == "__main__":
	output_edit_im()
	# output_data()
	# output_topics()
	# print(readCsvList(output_path, "mapping_marketing.csv"))
