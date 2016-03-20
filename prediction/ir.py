import os
from stemming.porter2 import stem
import re
import math
import numpy
from scipy.sparse import lil_matrix
import json
import operator
import random

inputPath = "input/"
outputPath = "output/"
stopwordFilename = "stopword.txt"
inputFilename = "data_labeled.json"
outputFilename = "data_predicted.json"
revisedFilename = "data_predicted_db.json"
docsFilename = "docs.json"


# Description:
def reviseDBformat():
	# add label3
	papers = readJson(outputPath+outputFilename)
	papers_cate = {"information management": list(), "marketing": list(), "transportation": list(), "om&or": list()}
	for paper in papers:
		cate = paper["fields"]["category"]
		papers_cate[cate].append(paper)
	for cate, cate_papers in papers_cate.items():
		samples = get_samples(50, len(cate_papers))
		# print(samples)
		for index, sample in enumerate(samples):
			pk = cate_papers[sample]["pk"]
			while papers[pk-1]["fields"]["is_phased1"]==True or papers[pk-1]["fields"]["is_phased2"]==True:
				sample+=1
				pk = cate_papers[sample]["pk"]
			papers[pk-1]["fields"]["phased3"] = 3
		count = 1
		for paper in cate_papers:
			pk = paper["pk"]
			# if papers[pk-1]["fields"]["is_phased1"]==True or papers[pk-1]["fields"]["is_phased2"]==True:
				# papers[pk-1]["fields"]["phased3"]=0
			if papers[pk-1]["fields"].get("phased3",0)==3:
				continue
			else:
				papers[pk-1]["fields"]["phased3"]=count
				count = count%2+1
	for paper in papers:
		paper["fields"]["time3"] = 0
		paper["fields"]["time4"] = 0
		paper["fields"]["label3"] = ""
		paper["fields"]["label4"] = ""
	writeJson(outputPath+revisedFilename, papers)

def get_samples(k, total):
	a = total/k
	b = random.random() * a
	numbers = list()
	for i in range(k):
		numbers.append(math.floor(a*i+b))
	return numbers


# Description: build the prediction model and update the prediction json file
def predictLabel():
	# testing要改成兩個都要
	# Data initialize
	papers = readJson(inputPath+inputFilename)
	doc_tf = getPaperTf(inputPath+docsFilename, papers)
	papers_cate = {"information management": {"training":list(), "testing": list()}, "marketing": {"training":list(), "testing": list()}, "transportation": {"training":list(), "testing": list()}, "om&or": {"training":list(), "testing": list()}}
	for paper in papers:
		if paper["fields"]["label_final"] != "":
			papers_cate[paper["fields"]["category"]]["training"].append(paper)
		# else:
		papers_cate[paper["fields"]["category"]]["testing"].append(paper)
	# Models 
	for cate, cate_papers in papers_cate.items():
		print(cate)
		training_indexs = [paper["pk"]-1 for paper in cate_papers["training"]]
		predict_indexs = [paper["pk"]-1 for paper in cate_papers["testing"]]
		training_data = [doc_tf[i] for i in training_indexs]
		predict_data = [doc_tf[i] for i in predict_indexs]
		# predict_data = training_data
		
		# naive bayes
		dictionary = buildDictoinaryDf(training_data)
		gts = [t["fields"]["label_final"] for t in cate_papers["training"]]

		labels = sorted(list(set(gts)))
		terms = sorted(dictionary.keys())
		n, nfeature, nlabel, nterm = len(training_data), 500, len(labels), len(terms)
		# writeDictionary(dictionary, "dict_"+cate)
		class_df = lil_matrix((nlabel+1, nterm+1))
		class_tf = lil_matrix((nlabel, nterm+1))
		label_distri = dict()
		
		# init df matrix, tf matrix and label_distri
		for index, doc in enumerate(training_data):
			label = gts[index]
			l_index = labels.index(label)
			label_distri[l_index] = label_distri.get(l_index,0) + 1
			for term in doc:
				# t_index = term_index_mapping[term]
				t_index = terms.index(term)
				class_df[l_index, t_index] = class_df[l_index, t_index] + 1
				class_tf[l_index, t_index] = class_tf[l_index, t_index] + doc[term]
		# get nc1, nt1 
		class_prob =  dict([(labels[k], (v/n)) for (k, v) in label_distri.items()])
		for i in range(nlabel):
			class_df[i,-1] = label_distri[i]
			for j in range(nterm):
				class_df[-1,j] += class_df[i,j]
		class_df[-1,-1] = n

		feature_indexs = featureSelection(class_df, nfeature, method="llr", score_method="local")
		class_term_prob = training(class_tf, nfeature, nlabel, feature_indexs, terms, labels)
		model = {"class": class_prob, "term": class_term_prob}
		writeJson("model_"+cate, model)
		predictions = testing(class_prob, class_term_prob, predict_data)
		# compare(gts, predictions)
		updatePapers(predictions, predict_indexs, papers)
	writeJson(outputPath+outputFilename, papers)
	# merge the prediction to the original file and write

def updatePapers(predictions, predict_indexs, papers):
	for index, pred in enumerate(predictions):
		papers[predict_indexs[index]]["fields"]["prediction"] = ";".join(pred)


def compare(gts, predictions):
	tp = 0
	for index, gt in enumerate(gts):
		pred = predictions[index]
		if gt in pred:
			tp+=1
	print("Accuracy:"+ str(tp/len(gts)))


def getPaperTf(filename, papers):
	stopwords = readStopwords()
	docs = readJson(filename)
	if len(docs)==0:
		for paper in papers:
			doc = getSentTf(paper["fields"]["abstract"], stopwords)
			docs.append(doc)
		writeJson(filename, docs)
	else:
		return docs


'''
Classification and feature selection
'''

def training(class_tf, nfeature, nlabel, feature_indexs, terms, labels):
	class_term_prob = dict()
	for i in range(nlabel):
		for j in feature_indexs:
			class_tf[i, -1] += class_tf[i, j]
	for i in range(nlabel):
		label = labels[i]
		class_term_prob[label] = dict()
		for j in feature_indexs:
			total_tf = class_tf[i, -1]
			term = terms[j]
			class_term_prob[label][term] = (class_tf[i,j]+1)/(total_tf+nfeature)
	return class_term_prob

# Description: read the training label_do
# Return: dictionary with label and docs
def readTrainingLabels(filename="training.txt"):
	doc_label_mapping = dict()
	training_indexs = list()
	nlabel = 0
	with open(filename, "r") as fi:
		for line in fi:
			numbers = line.strip().split(" ")
			label = int(numbers[0])-1
			nlabel+=1
			doc_indexs = [int(a)-1 for a in numbers[1:]]
			for doc_index in doc_indexs:
				doc_label_mapping[doc_index] = label
			training_indexs += doc_indexs
	training_indexs.sort()
	return nlabel, doc_label_mapping, training_indexs


def testing(class_prob, class_term_prob, testing_data):
	predictions = list()
	for i, doc in enumerate(testing_data):
		ranking = predict(doc, class_prob, class_term_prob)
		top =  [t[0] for t in ranking[0:3]]
		# print(top)
		predictions.append(top)
	return predictions

def predict(doc, class_prob, class_term_prob):
	prediction = int()
	scores = dict()
	for label in class_term_prob.keys():
		scores[label] = score(doc, class_term_prob[label], class_prob[label])
	prediction = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
	return prediction

def score(doc, probs, class_prob):
	score = math.log(class_prob)
	# score = 0
	for term, tf in doc.items():
		if term in probs:
			score += tf*math.log(probs[term])
	return score

# Description: Get the top important features by the method and score method
# Input: method: log likelyhood ratio, expected mutual information with local or global scoring function
# Return: feature indexs
def featureSelection(class_df, nfeature=500, method="llr", score_method="global"):
	feature_indexs = list()
	score_matrix = lil_matrix(class_df.shape)
	nlabel = class_df.shape[0]-1
	nterm = class_df.shape[1]-1
	for i in range(nlabel):
		for j in range(nterm):
			n = class_df[-1,-1]
			nt1 = class_df[-1,j]
			nc1 = class_df[i,-1]
			n11 = class_df[i,j]
			if method=="llr":
				score_matrix[i,j] = getTermClassLLR(class_df[-1,-1], class_df[-1,j], class_df[i,-1] ,class_df[i,j])
			elif method=="emi":
				score_matrix[i,j] = getTermClassEMI(class_df[-1,-1], class_df[-1,j], class_df[i,-1] ,class_df[i,j])
	feature_indexs = getFeatureIndex(score_matrix, nfeature, score_method)
	return feature_indexs

def getFeatureIndex(score_matrix, nfeature, score_method):
	if score_method == "global":
		return getGlobalScoreFeature(score_matrix, nfeature)
	else:
		return getLocalScoreFeature(score_matrix, nfeature)

def getLocalScoreFeature(score_matrix, nfeature):
	feature_indexs = set()
	class_score_index = dict()
	nlabel = score_matrix.shape[0]-1
	nterm = score_matrix.shape[1]-1
	for i in range(nlabel):
		score_index = zip(score_matrix[i,].toarray()[0], range(nterm))
		local_feature_indexs = [index for value, index in sorted(score_index, reverse=True)][:nfeature]
		class_score_index[i] = local_feature_indexs
	count = 0
	while len(feature_indexs) < nfeature:
		index = class_score_index[count%nlabel][math.floor(count/nlabel)]
		feature_indexs.add(index)
		count+=1
	return sorted(list(feature_indexs))

def getGlobalScoreFeature(score_matrix, nfeature):
	feature_indexs = list()
	nterm = score_matrix.shape[1]-1
	nlabel = score_matrix.shape[0]-1
	for i in range(nlabel):
		for j in range(nterm):
			score_matrix[-1,j] += score_matrix[i,j]
	score_index = zip(score_matrix[-1,].toarray()[0], range(nterm))
	feature_indexs = [index for value, index in sorted(score_index, reverse=True)][:nfeature]
	return feature_indexs


def getTermClassLLR(n, nt1, nc1, n11):
	slack = 0
	llr = 0
	n01 = nt1 - n11
	n10 = nc1 - n11
	n00 = n - nt1 - n10
	n11 += slack
	n01 += slack
	n10 += slack
	n00 += slack
	nt0 = n-nt1 + 2*slack
	nc0 = n-nc1 + 2*slack
	nt1 += 2*slack
	nc1 += 2*slack
	n += 4*slack
	if n11!=0:
		llr += n11*(math.log((n11+n10)/n)-math.log(n11/(n11+n10)))
	if n10!=0:
		llr += n10*(math.log((n10+n00)/n)-math.log(n10/(n11+n10)))
	if n01!=0:
		llr += n01*(math.log((n11+n10)/n)-math.log(n01/(n01+n00)))
	if n00!=0:
		llr += n00*(math.log((n10+n00)/n)-math.log(n00/(n01+n00)))
	return -2*llr


# Default: n = 195, nec1 = 15, nec0 = 180
def getTermClassEMI(n, nt1, nc1, n11):
	mi = 0
	nt0 = n-nt1
	nc0 = n-nc1
	n01 = nt1 - n11
	n10 = nc1 - n11
	n00 = n - nt1 - n10
	pt1 = nt1/n
	pt0 = nt0/n
	pc1 = nc1/n
	pc0 = nc0/n
	p11 = n11/n
	p01 = n01/n
	p10 = n10/n
	p00 = n00/n
	# print(n, net1, nec1, pet1ec1, pet1ec0, pet0ec1, pet0ec0)
	# et=1,ec=1 + et=1,ec=0 + et=0, ec=1, + et=0, ec=0
	if p11 != 0:
		mi += p11*math.log(p11/(pc1*pt1))
	if p01 != 0:
		mi += p01*math.log(p01/(pc0*pt1))
	if p10 != 0:
		mi += p10*math.log(p10/(pc1*pt0))
	if p00 != 0:
		mi += p00*math.log(p00/(pt0*pt0))
	return mi

'''
Uitility function
'''
# Description: get the stopwords by file
# Input: stopword filename
# Return: stopwords
def readStopwords():
	stopwords = list()
	with open(stopwordFilename, "r") as fs:
		for line in fs:
			stopwords.append(line.strip())
	return stopwords

def buildDictoinaryDf(docs):
	dictionary = dict()
	for doc in docs:
		for term in doc:
			if term not in dictionary.keys():
				dictionary[term] = 1
			else:
				dictionary[term] = dictionary[term]+1
	return dictionary

def splitData(docs, training_indexs):
	testing_indexs = [doc_index for doc_index in range(len(docs)) if doc_index not in training_indexs]
	training_data = [docs[doc_index] for doc_index in training_indexs]
	testing_data = [docs[doc_index] for doc_index in testing_indexs]
	return training_data, testing_data, testing_indexs

def getDocs():
	docs = list()
	stopwords = readStopwords()
	for i in range(1, 1095+1, 1):
		doc = getFileTf("IRTM/"+str(i)+".txt", stopwords)
		docs.append(doc)
	return docs

# Description: get the tf of doc 
# Input: filename
# Return: tf dictionary for one doc
def getFileTf(filename, stopwords):
	doc = dict()
	with open(filename, "r") as fi:
		for line in fi:
			for word in re.split("[^a-zA-Z0-9]", line.strip()):
				word = word.lower()
				if word != "" and word!="'" and stem(word) not in stopwords:
					if doc.get(stem(word), 0) == 0:
						doc[stem(word)] = 1
					else:
						doc[stem(word)] = doc[stem(word)]+1
	return doc

def getSentTf(sent, stopwords):
	doc = dict()
	for word in re.split("[^a-zA-Z0-9]", sent):
		word = word.lower()
		if word != "" and word!="'" and stem(word) not in stopwords:
			if doc.get(stem(word), 0) == 0:
				doc[stem(word)] = 1
			else:
				doc[stem(word)] = doc[stem(word)]+1
	return doc


# Description: get the dictionary of the docs
# Input: dictionary with df
# Output: dictionary file
# Return: t_index mapping, start from 1
def writeDictionary(dictionary, filename):
	with open(filename,"w") as fo:
		fo.write("t_index\tterm\tdf\n")
		i = 1
		for term in sorted(dictionary.keys()):
			fo.write(str(i)+"\t"+term+"\t"+str(dictionary[term])+"\n")
			i+=1

def readJson(filename):
	try:
		with open(filename, "r") as fi:
			return json.loads(fi.read())
	except:
		return list()

def writeJson(filename, result):
	with open(filename, "w") as fo:
		fo.write(json.dumps(result, indent=4))


if __name__ == "__main__":
	predictLabel()
	reviseDBformat()
