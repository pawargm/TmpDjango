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
		
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)

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
		resource_client = 	ResourceManagementClient(credentials,subid)

	except Exception as e:
		return HttpResponse(e)

	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			list_res.append(item)

	req.session.delete()
	return render(req,"lst_rg.html",{"lst_rg":list_res})


#checking to presence of netrc file
def check_netrc(req):

	msg = ""
	dic = {}
	if os.path.isfile("netrc"):
		info = netrc.netrc("netrc")
		#append Username to machine here we appaends just email 
		machine = "portal.azure.com"+"Gopal.Pawar@veritas.com"#We have to take username from database
		email = info.authenticators(machine)[0]
		password = info.authenticators(machine)[2]

		try:
			req.session['email'] = email
			req.session['password'] = password
			req.session['subid'] = "c721e2fd-94b3-4155-952e-60ba88bc1f6a"#this subid will taken from its database

			credentials = UserPassCredentials(email,password)
			resource_client = ResourceManagementClient(credentials,req.session['subid'])

			dic['vm'] = 0
			dic['nic'] = 0
			dic['vpn'] = 0
			dic['public_ip'] = 0
			dic['nsg'] = 0
			dic['strgAcc'] = 0

			cnt_rg = 0
			for rg in resource_client.resource_groups.list():
				cnt_rg += 1
				for item in resource_client.resource_groups.list_resources(rg.name):

					if "Microsoft.Compute/virtualMachines" == item.type:
						dic['vm'] += 1

					if "Microsoft.Network/networkInterfaces" == item.type:
						dic['nic'] += 1

					if "Microsoft.Network/publicIPAddresses" == item.type:
						dic['public_ip'] += 1

					if "Microsoft.Network/virtualNetworks" == item.type:
						dic['vpn'] += 1

					if "Microsoft.Network/networkSecurityGroups" == item.type:
						dic['nsg'] += 1

					if "Microsoft.Storage/storageAccounts" == item.type:
						dic['strgAcc'] += 1


			return render(req,'cards_azure_res.html',{"vm":dic['vm'],"nic":dic['nic'],"public_ip":dic['public_ip'],"vpn":dic["vpn"],"nsg":dic['nsg'],"strgAcc":dic['strgAcc'],"res_g":cnt_rg})
		except Exception as e:
			return HttpResponse(e)
	else:
		msg = "You have to login!"
		return render(req,'sample.html',{"message":msg})


#login from selection of access of cloud amezone or azure
def login_acc(req):

	return render(req,'choice_acc.html')

#showing options of azure cloud like storage acc,vm,vpn,resource group
def azure_res(req):

	return render(req,'cards_azure_res.html')

#it will shows list of vms
def lst_vm(req):

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
			if "Microsoft.Compute/virtualMachines" == item.type:
				list_res.append(item.name)

	return  render(req,"lst_rg.html",{"lst_rg":list_res,"lst":list_res})


#getting list of Storage account
def lst_storage_acc(req):

	lst_str_acc = []

	email = req.session['email']
	password = req.session['password']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			if "Microsoft.Storage/storageAccounts" == item.type:
				lst_str_acc.append(item.name)

	return render(req,'lst_rg.html',{"lst_rg":lst_str_acc})

#getting list of vpn

def lst_vpn(req):

	lst_vpn = []

	email = req.session['email']
	password = req.session['password']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			if "Microsoft.Network/virtualNetworks" == item.type:
				lst_vpn.append(item.name)

	return render(req,'lst_rg.html',{"lst_rg":lst_vpn})

#list out ips
def lst_pub_ips(req):

	lst_ips = []

	email = req.session['email']
	password = req.session['password']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			if "Microsoft.Network/publicIPAddresses" == item.type:
				lst_ips.append(item.name)

	return render(req,'lst_rg.html',{"lst_rg":lst_ips})

#list out nic 
def lst_nic(req):

	lst_nic = []

	email = req.session['email']
	password = req.session['password']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			if "Microsoft.Network/networkInterfaces" == item.type:
				lst_nic.append(item.name)

	return render(req,'lst_rg.html',{"lst_rg":lst_nic})

#List of networksecuritygroup
def lst_nsg(req):

	lst_nsg = []

	email = req.session['email']
	password = req.session['password']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			if "Microsoft.Network/networkSecurityGroups" == item.type:
				lst_nsg.append(item.name)

	return render(req,'lst_rg.html',{"lst_rg":lst_nsg})

#list out resource group
def lst_rg(req):

	lst_rg = []

	email = req.session['email']
	password = req.session['password']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for item in resource_client.resource_groups.list():
				lst_rg.append(item.name)

	return render(req,'lst_rg.html',{"lst_rg":lst_rg})



	


