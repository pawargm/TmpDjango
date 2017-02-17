import os
import netrc
import datetime
from newapp.form import LoginForm
from django.shortcuts import render
from django.http import HttpResponse
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import UserPassCredentials



email = None
password = None
subid = None

credentials = None



def current_datetime(req):
	now = datetime.datetime.now().date()
	html = "It is now %s "% now
	return HttpResponse(html)


def search_form(req):
	return render(req,'sample.html')


#Check Authentication of User
def authenticate(req):

	msg=""
	
	if 'email' in req.POST:
		email = req.POST['email']

		if email == "":
			return render(req,"validation_msg.html",{"message":"Plase fill email"})
	else:
		msg = "email is missing"
		return render(req,'validation_msg.html',{"message":msg})

	if 'password' in req.POST:
		password = req.POST['password']

		if password == "":
			msg = "password is missing"
			return render(req,'validation_msg.html',{"message":msg})
	else:
		msg = "password is missing"
		return render(req,'validation_msg.html',{"message":msg})


	if 'subid' in req.POST:
		subid = str(req.POST['subid'])

		if subid == "":
			msg = "subid is missing"
			return render(req,'validation_msg.html',{"message":msg})
	else:
		msg = "subid is missing"
		return render(req,'validation_msg.html',{"message":msg})
	

	try:
		req.session['email'] = email
		req.session['password'] = password
		req.session['subid'] = subid
		
		#credentials = UserPassCredentials(email,password)
		msg += "Valid user!!!!"
		
		fo = open("netrc","ab")
		machine = "portal.azure.com"+email
		str1 ="\nmachine "+machine+"\n"+"login "+email+"\n"+"password "+password

		fo.write(str1)
		return render(req,'validation_msg.html',{"message":msg})

	except Exception as e:
		
		msg += "EROOR: "
		msg += str(e)

		return render(req,'validation_msg.html',{"message":msg})


#list out ResourceGroup and list all the resources
def  list_resource(req):

	list_res = []

	email = req.session['email']
	password = req.session['password']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email, password)
		resource_client = ResourceManagementClient(credentials,subid)

	except Exception as e:
		return HttpResponse(e)

	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			list_res.append(item.name)

	req.session.delete()
	return render(req,"lst_rg.html",{"lst_rg":list_res})



def check_netrc(req):

	msg = ""
	if os.path.isfile("netrc"):
		info = netrc.netrc("netrc")
		#append Username to machine here we appaends just email 
		machine = "portal.azure.com"+"Gopal.Pawar@veritas.com"#We have to take username from database
		email = info.authenticators(machine)[0]
		password = info.authenticators(machine)[2]

		try:
			req.session['email'] = email
			req.session['password'] = password
			req.session['subid'] = "c721e2fd-94b3-4155-952e-60ba88bc1f6a"
			credentials = UserPassCredentials(email,password)

			msg += "Valid usr!!"

			return render(req,'validation_msg.html',{"message":msg})
		except Exception as e:
			msg += "EROOR: "
			msg += str(e)
			return render(req,'validation_msg.html',{"message":e})

	else:
		msg = "You have to login!"
		return render(req,'sample.html',{"message":msg})



def login_acc(req):

	return render(req,'choice_acc.html')



