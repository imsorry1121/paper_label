from django.shortcuts import render, redirect
from django.http import HttpResponse
from user.models import User
from paper.models import Paper
import json
import time
# Create your views here.


'''
Helper function
'''

def read_topics():
	im = read_json("public/topic_im.json")
	om = read_json("public/topic_om.json")
	transportation = read_json("public/topic_transportation.json")
	# marketing = read_json("/public/topic_marketing.json")
	marketing = dict()
	topics = {"information": im, "marketing": marketing, "om&or": om, "transportation": transportation}
	return topics


def read_json(filename):
	with open(filename, "r") as fo:
		result = json.loads(fo.read())
	return result

'''
Views
'''

category_mapping = {"information management": "information", "marketing": "marketing", "om&or": "om&or", "transportation": "transportation"}
url_mapping = {"information": "information management", "marketing": "marketing", "om&or": "om&or", "transportation": "transportation"}
topics = read_topics()

def login(request):
	# check if the two users finish its application

	context = dict()
	account = request.POST.get("account")
	pwd = request.POST.get("pwd")
	user = User.objects.filter(account=account, pwd=pwd)
	# User authentication
	if len(user) == 0:
		return render(request, 'login.html', context)
	else:
		# Check the numbers of unlabeled papers
		category = user[0].category
		url_category = category_mapping[category]
		uid = user[0].account[-1]
		pid = -1
		choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
		if len(choosed_papers.filter(label1="", label2=""))==0:
			return redirect("./compare/%s" %url_category)
		else:
			if uid == "1":
				for index, paper in enumerate(choosed_papers):
					if paper.label1 == "":
						pid = index
						break
			else:
				for index, paper in enumerate(choosed_papers):
					if paper.label2 == "":
						pid = index
						break
			if pid == -1:
				return redirect("./index/%s" % url_category)
			else:
				return redirect("./index/%s/%s/%s" %(url_category, uid, pid))


def index(request, url_category, uid, pid):
	context = dict()
	pid = int(pid)
	finish_percent = float()

	category = url_mapping[url_category]
	choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
	target_paper = choosed_papers[pid]
	total = len(choosed_papers)
	system_time = time.time()

	url_prefix = "/label/index/" + url_category +"/"+ uid+"/"
	prev_url = str()
	next_url = str()
	if pid == 0:
		prev_url = ""
		next_url = url_prefix + str(pid+1)
	elif pid == total:
		prev_url = url_prefix + str(pid-1)
		next_url = ""
	else:
		prev_url = url_prefix + str(pid-1)
		next_url = url_prefix + str(pid+1)
	label = str()
	if uid == "1":
		label = target_paper.label1
		unlabel_count = len(choosed_papers.filter(label1=""))
		finish_percent = (total-unlabel_count)/total*100
	elif uid == "2":
		label = target_paper.label2
		unlabel_count = len(choosed_papers.filter(label2=""))
		finish_percent = (total-unlabel_count)/total*100
	elif uid == "3":
		label = target_paper.label_final
		unaligned_count = len(choosed_papers.filter(label_final=""))
		finish_percent = (total-unaligned_count)/total*100
	else:
		return HttpResponse('<h1>Page was found</h1>')

	# target_paper.keywords_plus = target_paper.keywords_plus.split(";")
	context = {"uid": uid, "pid": pid, "category": category, "paper": target_paper, "prev_url": prev_url, "next_url": next_url, "bar": finish_percent, "url_category": url_category, "label": label, "index": pid+1, "sub_cates": topics[url_category], "time": system_time}
	return render(request, 'index.html', context)



def update(request, url_category, uid, pid):
	category = url_mapping[url_category]
	label = request.GET["label"]
	choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
	target_paper = choosed_papers[int(pid)]
	if str(uid)=="1":
		target_paper.label1 = label
	elif uid=="2":
		target_paper.label2 = label
	elif uid=="3":
		target_paper.label_final = label
	else:
		return HttpResponse('<h1>Page was found</h1>')
	if target_paper.label1 == target_paper.label2:
		target_paper.label_final = label
	target_paper.save()
	print("save success")
	return HttpResponse("success")

def list(request, url_category, uid):
	# return paper list
	if uid != "1" and uid != "2":
		return HttpResponse('<h1>Page was found</h1>')
	context = dict()
	category = url_mapping[url_category]
	choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
	context["category"] = category
	context["url_category"] = url_category
	context["papers"] = choosed_papers
	context["uid"] = uid
	count1 = int()
	count2 = int()
	total = len(choosed_papers)
	for paper in choosed_papers:
		if paper.label1 != "":
			count1+=1
		if paper.label2 != "":
			count2+=1
	context["stat"] = {"finish1": count1, "finish2": count2, "total": total, "percent1": count1/total*100, "percent2": count2/total*100}
	return render(request, "list.html", context)

def compare(request, url_category):
	context = dict()
	category = url_mapping[url_category]
	choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
	context["category"] = category
	context["url_category"] = url_category
	context["papers"] = choosed_papers
	count1 = int()
	count2 = int()
	unalignment_count = int()
	total = len(choosed_papers)
	for paper in choosed_papers:
		if paper.label1 != "" and paper.label2 != "" and paper.label1 != paper.label2 and paper.label_final == "":
			unalignment_count +=1
	context["stat"] = {"total": total, "unalignment": unalignment_count, "unalignment_ratio": unalignment_count/total*100}
	context["sub_cates"] = topics[url_category]
	context["uid"] = "3"
	return render(request, "compare.html", context)
