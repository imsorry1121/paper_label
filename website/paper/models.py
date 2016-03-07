from django.db import models

# Create your models here.
class Paper(models.Model):
	category = models.CharField(max_length=255)
	isi = models.CharField(max_length=30)
	author = models.CharField(max_length=500)
	title = models.CharField(max_length=255)
	journal = models.CharField(max_length=255)
	year = models.CharField(max_length=10)
	month = models.CharField(max_length=10)
	volume = models.CharField(max_length=10, default="")
	number = models.CharField(max_length=10)
	pages = models.CharField(max_length=10)
	abstract = models.TextField()
	type = models.CharField(max_length=30, default="")
	keyword = models.TextField(default="")
	keywords_plus = models.TextField(default="")
	web_of_science_categories = models.CharField(max_length=225, default="")
	is_phased1 = models.BooleanField(default=False)
	is_phased2 = models.BooleanField(default=False)
	phased3 = models.IntegerField(default=0)
	label1 = models.CharField(max_length=255, default="")
	label2 = models.CharField(max_length=255, default="")
	label_final = models.CharField(max_length=255, default="")
	time1 = models.FloatField(default=0)
	time2 = models.FloatField(default=0)
	time_final = models.FloatField(max_length=255, default=0)
	prediction = models.TextField(default="")
	


