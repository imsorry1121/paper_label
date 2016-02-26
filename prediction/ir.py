import os
from stemming.porter2 import stem
import re
import math
import numpy
from scipy.sparse import lil_matrix
import json
import operator

stopwordFilename = "stopword.txt"
dictionaryFilename = "dictionary.txt"
inputFilename = "input/paper_dump.json"
docsFilename = "input/docs.json"


def predictLabel():
	papers = readJson(inputFilename)
	docs = getPaperTf(docsFilename, papers)


	papers_cate = {"information management": {"training":list(), "testing": list()}, "marketing": {"training":list(), "testing": list()}, "transportation": {"training":list(), "testing": list()}, "om&or": {"training":list(), "testing": list()}}
	dictionary = dict()
	for paper in papers:
		if paper["fields"]["label_final"] != "":
			papers_cate[paper["fields"]["category"]]["training"].append(paper)
		else:
			papers_cate[paper["fields"]["category"]]["testing"].append(paper)
	print("over loading")
	# build each dictionary and its idf
	# for cate, cate_papers in papers_cate.items():
	cate = "information management"
	cate_papers = papers_cate[cate]
	training_indexs = [paper["pk"]-1 for paper in cate_papers["training"]]
	predict_indexs = [paper["pk"]-1 for paper in cate_papers["testing"]]
	training_data = [docs[i] for i in training_indexs]
	testing_data = training_data
	predict_data = [docs[i] for i in predict_indexs]


	# naive bayes
	dictionary_train = buildDictoinaryDf(training_data)
	nterm = len(dictionary_train)
	labels = sorted(list(set([t["fields"]["label_final"] for t in cate_papers["training"]])))
	nlabel = len(labels)
	print(labels)
	nfeature = 100
	n = len(training_data)
	label_distri = dict()
	label_index_mapping = dict((v,k) for k,v in enumerate(labels))
	term_index_mapping = writeDictionary(dictionary_train)
	index_term_mapping = dict((v,k) for k,v in term_index_mapping.items())
	class_df = lil_matrix((nlabel+1, nterm+1))
	class_tf = lil_matrix((nlabel, nterm+1))
	class_term_prob = dict()

	# init df matrix and tf matrix
	for index, doc in enumerate(training_data):
		label = cate_papers["training"][index]["fields"]["label_final"]
		l_index = label_index_mapping[label]
		label_distri[l_index] = label_distri.get(l_index,0) + 1
		for term in doc:
			t_index = term_index_mapping[term]
			class_df[l_index, t_index] = class_df[l_index, t_index] + 1
			class_tf[l_index, t_index] = class_tf[l_index, t_index] + doc[term]
	# get nc1, nt1 
	for i in range(nlabel):
		class_df[i,-1] = label_distri[i]
		for j in range(nterm):
			class_df[-1,j] += class_df[i,j]
	class_df[-1,-1] = n
	# best
	feature_indexs = featureSelection(class_df, nfeature, method="llr", score_method="local")
	training(class_term_prob, class_tf, nfeature, nlabel, feature_indexs, index_term_mapping, labels)
	testing(class_term_prob, testing_data, labels)

	# use the prediction result to update 
# need to add class prob

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

def training(class_term_prob, class_tf, nfeature, nlabel, feature_indexs, index_term_mapping, labels):
	for i in range(nlabel):
		for j in feature_indexs:
			class_tf[i, -1] += class_tf[i, j]
	for i in range(nlabel):
		label = labels[i]
		class_term_prob[label] = dict()
		for j in feature_indexs:
			total_tf = class_tf[i, -1]
			term = index_term_mapping[j]
			class_term_prob[label][term] = (class_tf[i,j]+1)/(total_tf+nfeature)
	with open("model", "w") as fo:
		fo.write(json.dumps(class_term_prob, indent=4))

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


def testing(class_term_prob, testing_data, labels):
	with open("output.txt", "w") as fo:
		for i, doc in enumerate(testing_data):
			ranking = predict(doc, class_term_prob)
			top = ranking[0][0]
			fo.write(top+'\n')

def predict(doc, class_term_prob):
	prediction = int()
	scores = dict()
	for label in class_term_prob.keys():
		scores[label] = score(doc, class_term_prob[label])
	prediction = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
	print(prediction)
	return prediction

def score(doc, probs):
	score = float()
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
def writeDictionary(dictionary):
	# sort by key
	termIndex = dict()
	with open(dictionaryFilename,"w") as fo:
		# header
		fo.write("t_index\tterm\tdf\n")
		i = 1
		for term in sorted(dictionary.keys()):
			fo.write(str(i)+"\t"+term+"\t"+str(dictionary[term])+"\n")
			termIndex[term] = i-1
			i+=1
	return termIndex

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
