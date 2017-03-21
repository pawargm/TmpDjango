from __future__ import unicode_literals

from django.db import models
from passlib.hash import pbkdf2_sha256



class Azure_Account(models.Model):


	vmail = models.CharField(max_length = 50)
	vpass = models.CharField(max_length = 50)
	vsubid = models.CharField(max_length = 50)

	def __str__(self):
		return self.vmail

class Account(models.Model):

	firstname = models.CharField(max_length = 50)
	lastname = models.CharField(max_length = 50)
	username = models.CharField(max_length = 50, unique = True)
	mail = 	models.CharField(max_length =  50)
	password = models.CharField(max_length = 20)

	azure_acc = models.OneToOneField(Azure_Account,on_delete=models.CASCADE,primary_key=True)



	def __str__(self):
		return self.username
