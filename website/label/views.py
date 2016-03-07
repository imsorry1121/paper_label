from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
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
	marketing = read_json("public/topic_marketing.json")
	topics = {"information": im, "marketing": marketing, "om": om, "transportation": transportation}
	return topics


def read_json(filename):
	with open(filename, "r") as fo:
		result = json.loads(fo.read())
	return result

def get_om_topics(cate_topics):
	topics = cate_topics[:-1]
	topics = topics+om_special_topics
	return topics


'''
Views
'''
category_mapping = {"information management": "information", "marketing": "marketing", "om&or": "om", "transportation": "transportation"}
url_mapping = {"information": "information management", "marketing": "marketing", "om": "om&or", "transportation": "transportation"}
om_special_topics = [{"title": "Not relevant", "topics": [{"title":"Relevant to IM"}, {"title":"Relevant to Transportation"}, {"title":"Relevant to Marketing"}, {"title":"Not Relevant to All Fields"}]}]
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
		uid = user[0].index
		pid = -1
		# choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
		users = User.objects.filter(category=category)
		if (users[0].is_phased1):
			choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
		elif (users[0].is_phased2):
			choosed_papers = Paper.objects.filter(category=category, is_phased2=True)
		else:
			choosed_papers = Paper.objects.filter(category=category, phased3__in=[uid, 3])
		total = len(choosed_papers)
		# if need to redirect to compare page or list, index page
		if (len(choosed_papers.filter(~Q(label1="")))== total and len(choosed_papers.filter(~Q(label2=""))) == total):
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
				return redirect("./list/%s/%s" % (url_category, uid))
			else:
				return redirect("./index/%s/%s/%s" %(url_category, uid, pid))


def index(request, url_category, uid, pid):
	context = dict()
	pid = int(pid)
	finish_percent = float()

	category = url_mapping[url_category]
	users = User.objects.filter(category=category)
	if (users[0].is_phased1):
		phase = 1
		choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
	elif(users[0].is_phased2):
		choosed_papers = Paper.objects.filter(category=category, is_phased2=True)
		phase = 2
	else:
		phase = 3
		choosed_papers = Paper.objects.filter(category=category, phased3__in=[uid, 3])
	target_paper = choosed_papers[pid]
	total = len(choosed_papers)
	system_time = time.time()
	preds = target_paper.prediction.split(",")
	url_prefix = "/label/index/" + url_category +"/"+ uid+"/"
	prev_url = str()
	next_url = str()
	# check url
	if pid == 0:
		prev_url = ""
		next_url = url_prefix + str(pid+1)
	elif pid == total-1:
		prev_url = url_prefix + str(pid-1)
		next_url = ""
	else:
		prev_url = url_prefix + str(pid-1)
		next_url = url_prefix + str(pid+1)
	label = str()
	if uid == "1":
		users = User.objects.filter(index=uid, category=category)
		label = target_paper.label1
		unlabel_count = len(choosed_papers.filter(label1=""))
		finish_percent = (total-unlabel_count)/total*100
	elif uid == "2":
		users = User.objects.filter(index=uid, category=category)
		label = target_paper.label2
		unlabel_count = len(choosed_papers.filter(label2=""))
		finish_percent = (total-unlabel_count)/total*100
	elif uid == "3":
		users = User.objects.filter(category=category)
		label = target_paper.label_final
		unaligned_count = len(choosed_papers.filter(label_final=""))
		finish_percent = (total-unaligned_count)/total*100
	else:
		return HttpResponse('<h1>Page was found</h1>')
	cate_topics = topics[url_category]
	# check om&or management science
	if url_category=="om" and target_paper.journal == "MANAGEMENT SCIENCE":
		cate_topics = get_om_topics(cate_topics)
	context = {"uid": uid, "pid": pid, "category": category, "users": users, "paper": target_paper, "prev_url": prev_url, "next_url": next_url, "bar": finish_percent, "url_category": url_category, "label": label, "index": pid+1, "sub_cates": cate_topics, "time": system_time, "phase": phase, "preds":preds}
	return render(request, 'index.html', context)



def update(request, url_category, uid, pid, label):
	category = url_mapping[url_category]
	print(label)
	time_diff = int(time.time()) - int(request.GET["time"])
	users = User.objects.filter(category=category)
	if (users[0].is_phased1):
		phase=1
		choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
	elif(users[0].is_phased2):
		phase=2
		choosed_papers = Paper.objects.filter(category=category, is_phased2=True)
	else:
		phase=3
		choosed_papers = Paper.objects.filter(category=category, phased3__in=[uid,3])
	target_paper = choosed_papers[int(pid)]
	print(time_diff)

	if str(uid)=="1":
		target_paper.label1 = label
		target_paper.time1 = time_diff
	elif uid=="2":
		target_paper.label2 = label
		target_paper.time2 = time_diff
	elif uid=="3":
		target_paper.label_final = label
		target_paper.time_final = time_diff
	else:
		return HttpResponse('<h1>Page was found</h1>')
	if target_paper.label1!="" and target_paper.label1 == target_paper.label2:
		target_paper.label_final = label
		target_paper.time_final = 0
	target_paper.save()
	print("save success")
	return HttpResponse("success")

def list(request, url_category, uid):
	# return paper list
	if uid != "1" and uid != "2":
		return HttpResponse('<h1>Page was found</h1>')
	context = dict()
	category = url_mapping[url_category]
	users = User.objects.filter(category=category)
	if (users[0].is_phased1):
		choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
		phase = 1
		context["title"] = category.upper() + " (Phase 1-"+str(phase)+")"
	elif(users[0].is_phased2):
		choosed_papers = Paper.objects.filter(category=category, is_phased2=True)
		phase = 2
		context["title"] = category.upper() + " (Phase 1-"+str(phase)+")"
	else:
		phase = 3
		context["title"] = category.upper()
		choosed_papers = Paper.objects.filter(category=category, phased3__in=[uid,3])
	context["category"] = category
	context["phase"] = phase
	context["url_category"] = url_category
	context["papers"] = choosed_papers
	context["uid"] = uid
	count1 = 0
	count2 = 0
	if phase==3:
		total = len(choosed_papers)
		choosed_papers1 = Paper.objects.filter(category=category, phased3__in=[1,3]).filter(~Q(label1=""))
		choosed_papers2 = Paper.objects.filter(category=category, phased3__in=[2,3]).filter(~Q(label2=""))
		count1 = len(choosed_papers1)
		count2 = len(choosed_papers2)
	else:
		total = len(choosed_papers)
		for paper in choosed_papers:
			if paper.label1 != "":
				count1+=1
			if paper.label2 != "":
				count2+=1
	context["stat"] = {"user1": users[0].name, "user2": users[1].name, "finish1": count1, "finish2": count2, "total": total, "percent1": count1/total*100, "percent2": count2/total*100}
	return render(request, "list.html", context)

def compare(request, url_category):
	context = dict()
	category = url_mapping[url_category]
	users = User.objects.filter(category=category)
	if (users[0].is_phased1):
		choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
		phase = 1
	else:
		choosed_papers = Paper.objects.filter(category=category, is_phased2=True)
		phase = 2
	total = len(choosed_papers)
	# if the choosed_papers not all done then redirect to login page
	if not (len(choosed_papers.filter(~Q(label1="")))== total and len(choosed_papers.filter(~Q(label2=""))) == total):
		return redirect("/label/login")
	# choosed_papers = Paper.objects.filter(category=category, is_phased1=True)
	context["category"] = category
	context["title"] = category.upper() + " (Phase 1-"+str(phase)+")"
	context["url_category"] = url_category
	context["papers"] = choosed_papers
	users = User.objects.filter(category=category)
	count1 = int()
	count2 = int()
	unalignment_count = int()
	total = len(choosed_papers)
	for paper in choosed_papers:
		if paper.label1 != "" and paper.label2 != "" and paper.label1 != paper.label2 and paper.label_final == "":
			unalignment_count +=1
	context["stat"] = {"user1": users[0].name, "user2": users[1].name, "total": total, "unalignment": unalignment_count, "unalignment_ratio": unalignment_count/total*100}
	context["sub_cates"] = topics[url_category]
	context["phase"] = phase
	context["uid"] = "3"
	return render(request, "compare.html", context)

def next(request, url_category):
	category = url_mapping[url_category]
	users = User.objects.filter(category=category)
	for user in users:
		user.is_phased1 = False
		user.is_phased2 = True
		user.save()
	return render(request, "login.html")	

