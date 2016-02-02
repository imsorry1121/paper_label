from django.db import models

# Create your models here.
class User(models.Model):
	name = models.CharField(max_length=255, default="")
	account = models.CharField(max_length=255)
	pwd = models.CharField(max_length=255)
	category = models.CharField(max_length=255)
	index = models.CharField(max_length=20, default="")

