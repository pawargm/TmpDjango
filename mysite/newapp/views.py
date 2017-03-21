import os
import netrc
import datetime
from haikunator import Haikunator
from passlib.hash import pbkdf2_sha256
from newapp.form import LoginForm
from .models import Account
from .models import Azure_Account
from django.shortcuts import render
from django.http import HttpResponse
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import UserPassCredentials
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

from django.contrib.auth.decorators import login_required
import jsonpickle




@login_required


def current_datetime(req):
	now = datetime.datetime.now().date()
	html = "It is now %s "% now
	return HttpResponse(html)


def search_form(req):
	return render(req,'sample.html')


#login from selection of access of cloud amezone or azure
def index(req):
	req.session['loginstatus'] = "logedout"
	req.session['loginazure'] = 'notset'
	return render(req,'index.html')


#getting login form for main account of PRMS
def signup_acc(req):

	return  render(req,'signup_acc.html')

def login_acc(req):

	return render(req,'login_acc.html')


#showing options of azure cloud like storage acc,vm,vpn,resource group
def azure_res(req):

	return render(req,'cards_azure_res.html')


#login to azure account
def login_to_azure(req):

	try:
		#here check if already login to azure then loginazure should be at value 'set'
		if req.session['loginazure'] == 'set':
			return check_netrc(req)

		username = req.session['username']
		acc_obj = Account.objects.get(username = username)
		acc_obj.azure_acc.vmail

	except Exception as e:

		return render(req,"login_to_azure.html")
	else:

		return render(req,"login_azure_only_pass.html")	

#after loginto azure by using only password
def login_azure_only_pass(req):

	try:
		pwd = req.POST['password']

		username = req.session['username']
		req.session['azure_pwd'] = pwd

		acc_obj = Account.objects.get(username = username)

		enc_pass = str(acc_obj.azure_acc.vpass)
		mail = str(acc_obj.azure_acc.vmail)

		req.session['email'] = mail
		req.session['subid'] = str(acc_obj.azure_acc.vsubid)

		if pbkdf2_sha256.verify(pwd,enc_pass):
			return check_netrc(req)
		else:
			HttpResponse("password is worng")
	except Exception as e:
		return HttpResponse("You have to login")





#Login to Azure Account
def login_to_azure_account(req):

	mail = req.POST['mail']

	password = req.POST['password']



	enc_pass = pbkdf2_sha256.encrypt(password,rounds=12000,salt_size=32)

	try:
		acc_obj = Account.objects.get(mail=mail)
		acc_obj.azure_acc.vmail
		
	except Exception as e:
		
		acc_obj.azure_acc = Azure_Account(vmail = mail,vpass = enc_pass,vsubid = req.POST['subid'])
		acc_obj.azure_acc.save()

		req.session['mail'] = mail
		req.session['azure_pwd'] = password
		req.session['subid'] = req.POST['subid']

		#check_netrc(req)
		return HttpResponse("Azure Account get filled")
	else:
		return HttpResponse("already has azure account")	
		





#for signup code
def make_account(req):

	password = req.POST['password']

	enc_pass = pbkdf2_sha256.encrypt(password,rounds=12000,salt_size=32)

	mail = req.POST['mail']

	try:
		Account.objects.get(username = req.POST['username'])

	except Exception as e:

		acc_obj = Account( firstname = req.POST['first_name'],lastname = req.POST['last_name'], username = req.POST['username'],mail = mail,password = enc_pass)
		acc_obj.save()
		return HttpResponse("You are get registered please make login!")

	else:
		return HttpResponse("Choose another username!username already present")#handle sessions

#login code of main account
def check_account(req):

	try:

		if req.session['loginazure'] == 'set':
			return render(req,"index_loged_in.html")
		
		username = req.POST['username']
		password = req.POST['password']

		acc_obj = Account.objects.get(username=username)
	
		pass_obj = str(acc_obj.password)
		
		if pbkdf2_sha256.verify(password,pass_obj):

			req.session['username'] = username
			return render(req,"index_loged_in.html")

		else:
			return HttpResponse("You cannot loged in!")

	except Exception as e:
		return HttpResponse("You cannot loged in!")	


def logout_main_acc(req):

	for key in req.session.keys():
		del req.session[key]
	return render(req,"index.html")


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
		

		#fo = open("netrc","ab")
		#machine = "portal.azure.com"+email
		#str1 ="\nmachine "+machine+"\n"+"login "+email+"\n"+"password "+password

		#fo.write(str1)

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


	#if req.session['loginstatus'] == 'logedout':
		#return render(req,'signup_acc.html',{"message":"You have to singup first"})

	#else:


		msg = ""
		dic = {}
		'''if os.path.isfile("netrc"):
			info = netrc.netrc("netrc")
			#append Username to machine here we appaends just email 
			machine = "portal.azure.com"+"Gopal.Pawar@veritas.com"#We have to take username from database
			email = info.authenticators(machine)[0]
			password = info.authenticators(machine)[2]
		'''
		try:
				'''req.session['email'] = email
				req.session['password'] = password
				req.session['subid'] = "c721e2fd-94b3-4155-952e-60ba88bc1f6a"#this subid will taken from its database
				'''

				email = req.session['email']
				pwd_azure = req.session['azure_pwd']
				subid = str(req.session['subid'])




				credentials = UserPassCredentials(email,pwd_azure)
				resource_client = ResourceManagementClient(credentials,subid)
				network_client = NetworkManagementClient(credentials,subid)
				storage_client = StorageManagementClient(credentials,subid)
				compute_client = ComputeManagementClient(credentials,subid)


				req.session['credentials'] = jsonpickle.encode(credentials)
				req.session['resource_client'] = jsonpickle.encode(resource_client)
				req.session['network_client'] = jsonpickle.encode(network_client)
				req.session['storage_client'] = jsonpickle.encode(storage_client)
				req.session['compute_client'] = jsonpickle.encode(compute_client)



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



				req.session['loginazure'] = 'set'
				#req.session['credentials'] = credentials
				return render(req,'cards_azure_res.html',{"vm":dic['vm'],"nic":dic['nic'],"public_ip":dic['public_ip'],"vpn":dic["vpn"],"nsg":dic['nsg'],"strgAcc":dic['strgAcc'],"res_g":cnt_rg})
		except Exception as e:
				return HttpResponse("ERROR"+str(e))
		else:
			msg = "You have to login!"
			return render(req,'sample.html',{"message":msg})




#it will shows list of vms
def lst_vm(req):

	list_res = []

	email = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])

	credentials_obj = jsonpickle.decode(req.session['credentials'])

	try:
		#credentials = credentials_obj
		resource_client =  jsonpickle.decode(req.session['resource_client'])#ResourceManagementClient(credentials_obj,subid)

		
		for rg in resource_client.resource_groups.list():
			for item in resource_client.resource_groups.list_resources(rg.name):
				str_name = ""
				if "Microsoft.Compute/virtualMachines" == item.type:
					str_name = item.name + "," +rg.name
					list_res.append(str_name)

	except Exception as e:
		raise

	return  render(req,"lst_vm.html",{"lst_rg":list_res,"lst":list_res})


#getting list of Storage account
def lst_storage_acc(req):

	lst_str_acc = []
	

	email = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			str_name = ""
			if "Microsoft.Storage/storageAccounts" == item.type:
				str_name = item.name + "," + rg.name
				lst_str_acc.append(str_name)
				

	return render(req,'lst_storage_acc.html',{"lst_rg":lst_str_acc})

#getting list of vpn

def lst_vpn(req):

	lst_vpn = []

	email = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			str_name = ""
			if "Microsoft.Network/virtualNetworks" == item.type:
				str_name = item.name + "," + rg.name
				lst_vpn.append(str_name)

	return render(req,'lst_vpn.html',{"lst_rg":lst_vpn})

#list out ips
def lst_pub_ips(req):

	lst_ips = []

	email = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			str_name = ""
			if "Microsoft.Network/publicIPAddresses" == item.type:
				str_name = item.name + "," + rg.name
				lst_ips.append(str_name)

	return render(req,'lst_public_ip.html',{"lst_rg":lst_ips})

#list out nic 
def lst_nic(req):

	lst_nic = []

	email = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			str_name = ""
			if "Microsoft.Network/networkInterfaces" == item.type:
				str_name = item.name + "," + rg.name
				lst_nic.append(str_name)

	return render(req,'lst_nic.html',{"lst_rg":lst_nic})

#List of networksecuritygroup
def lst_nsg(req):

	lst_nsg = []

	email = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for rg in resource_client.resource_groups.list():
		for item in resource_client.resource_groups.list_resources(rg.name):
			str_name=""
			if "Microsoft.Network/networkSecurityGroups" == item.type:
				str_name = item.name + "," + rg.name
				lst_nsg.append(str_name)

	return render(req,'lst_nsg.html',{"lst_rg":lst_nsg})

#list out resource group
def lst_rg(req):

	lst_rg = []

	email = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])

	try:
		credentials = UserPassCredentials(email,password)
		resource_client = ResourceManagementClient(credentials,subid)
	except Exception as e:
		return HttpResponse(e)
	
	for item in resource_client.resource_groups.list():
				lst_rg.append(item.name)

	return render(req,'lst_rg.html',{"lst_rg":lst_rg})



def call_form(req):

	return render(req,'form.html')

def backj(req):

	'''if os.path.isfile("netrc"):
		info = netrc.netrc("netrc")
		#append Username to machine here we appaends just email 
		machine = "portal.azure.com"+"Gopal.Pawar@veritas.com"#We have to take username from database
		email = info.authenticators(machine)[0]
		password = info.authenticators(machine)[2]
		subid = "c721e2fd-94b3-4155-952e-60ba88bc1f6a"

		haikunator = Haikunator()'''
	email = req.POST['email']
	password = req.POST['azure_pwd']
	subid = req.POST['subid']


	try:

		credentials = UserPassCredentials(email,password)

	except Exception as e:
			HttpResponse(e)


	LOCATION = req.POST['location']

	GROUP_NAME = req.POST['resgroup']

	VNET_NAME = req.POST['vpn_name']
	SUBNET_NAME = req.POST['subnet_name']

	OS_DISK_NAME = 'vsample-osdisk'

	STORAGE_ACCOUNT_NAME = req.POST['storage_acc_name']
	IP_CONFIG_NAME = 'vsample-ip-config'
	NIC_NAME = req.POST['nic_name']

	USERNAME = req.POST['admin_name']
	PASSWORD = req.POST['admin_pass']
	VM_NAME = req.POST['vm_name']

	VM_REFERENCE = {

		'linux': {
        'publisher': 'Canonical',
        'offer': 'UbuntuServer',
        'sku': '16.04.0-LTS',
        'version': 'latest'
    	},

    	'windows': {
        'publisher': 'MicrosoftWindowsServerEssentials',
        'offer': 'WindowsServerEssentials',
        'sku': 'WindowsServerEssentials',
        'version': 'latest'
    	}
	}

	resource_client = ResourceManagementClient(credentials,subid)
	compute_client = ComputeManagementClient(credentials,subid)
	storage_client = StorageManagementClient(credentials,subid)
	network_client = NetworkManagementClient(credentials,subid)

	#Creating Storage Account 

	storage_async_operation = storage_client.storage_accounts.create(GROUP_NAME,STORAGE_ACCOUNT_NAME,

																		{
																				'sku':{'name':req.POST['replication_type']},
																				'kind':'storage',
																				'location':LOCATION

																		}

																	)

	storage_async_operation.wait()

	#Creating NIC 

	#creating public ip for virtual machine

	public_ip_parameters = {
							'location':LOCATION,
							 'public_ip_allocation_method':'static',
							 'dns_settings':{'domain_name_label':req.POST['domain_label']},
							 'idle_timeout_in_minutes': 4
						
						}

	public_ip_creation = network_client.public_ip_addresses.create_or_update(GROUP_NAME,req.POST['public_ip_name'],public_ip_parameters)
	public_ip_info = public_ip_creation.result()


	#creating Virtual Network
	async_vnet_creation = network_client.virtual_networks.create_or_update(GROUP_NAME,VNET_NAME,

																				{
																					'location':LOCATION,
																					'address_space':{'address_prefixes': [req.POST['vpn_address']]}

																				}	
																			)
	async_vnet_creation.wait()

	#creating Subnet
	async_subnet_creation = network_client.subnets.create_or_update(GROUP_NAME,VNET_NAME,SUBNET_NAME,{'address_prefix':req.POST['subnet_address']})

	subnet_info = async_subnet_creation.result()
	

	

	#creating NIC

	async_nic_creation = network_client.network_interfaces.create_or_update(GROUP_NAME,NIC_NAME,

																				{
																					'location':LOCATION,
																					'ip_configurations':[{'name':IP_CONFIG_NAME,'subnet':{'id':subnet_info.id},'public_ip_address':{'id':public_ip_info.id}}]

																				}


																			)

	nic = async_nic_creation.result()

	os_parameter = VM_REFERENCE[req.POST['vm_type']]

	vm_parameters = 	{
						'location': LOCATION,
						'os_profile':{
									'computer_name': VM_NAME,
									'admin_username': USERNAME,
									'admin_password': PASSWORD

									},
						'hardware_profile':{'vm_size': 'Standard_DS1'},
						'storage_profile':{
											'image_reference':{'publisher': os_parameter['publisher'],'offer': os_parameter['offer'],'sku': os_parameter['sku'],'version': os_parameter['version']},
											'os_disk':{

													'name': OS_DISK_NAME,
													'caching': 'None',
													'create_option': 'fromImage',
													'vhd':{	'uri': 'https://{}.blob.core.windows.net/vhds/{}.vhd'.format(STORAGE_ACCOUNT_NAME, VM_NAME+haikunator.haikunate())}

													}

											},
						'network_profile':{'network_interfaces':[{'id':nic.id}]},

						}





	async_vm_creation = compute_client.virtual_machines.create_or_update(GROUP_NAME,VM_NAME,vm_parameters)
	async_vm_creation.wait()


	#Attach data disks
	async_vm_update = compute_client.virtual_machines.create_or_update(GROUP_NAME,VM_NAME,

																			{
																				'location':LOCATION,
																				'storage_profile':{'data_disks':[{'name':'mydatadisk1','disk_size_gb':1,'lun':0,'vhd':{'uri':"http://{}.blob.core.windows.net/vhds/mydatadisk1.vhd".format(STORAGE_ACCOUNT_NAME)},'create_option':'Empty'}]
																									}


																				

																			}
																		)



	async_vm_update.wait()
	
	#Get one VM by name
	Virtual_machine = compute_client.virtual_machines.get(GROUP_NAME,VM_NAME)

	#Start VM
	async_vm_start = compute_client.virtual_machines.start(GROUP_NAME,VM_NAME)
	async_vm_start.wait()

	return HttpResponse("Succefully created")



#new code

def output(req):

	return render(req,'form_label.html')

def output1(req):

	lst = req.GET.getlist('abc')

	return HttpResponse(lst)


#deletion code 

#this function for deletion of storage account
def delstorage(req):



	mail = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])
	

	credentials = UserPassCredentials(mail,password)

	storage_client = StorageManagementClient(credentials,subid)
	resource_client = ResourceManagementClient(credentials,subid)


	lst_del_str = req.GET.getlist('abc')


	try:

		'''for rg in resource_client.resource_groups.list():
			for item in resource_client.resource_groups.list_resources(rg.name):

				if "Microsoft.Storage/storageAccounts" == item.type and item.name in lst_del_str:

					storage_client.storage_accounts.delete(rg.name,item.name)
		'''
		
		lst = lst_del_str[0].split(",")
		storage_client.storage_accounts.delete(lst[1],lst[0])

	except Exception as e:

		return HttpResponse(e)
	else:
		return HttpResponse("Successfully deleted")



#this function is for deletion of nics
def delnic(req):

	mail = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])
	

	credentials = UserPassCredentials(mail,password)

	network_client = NetworkManagementClient(credentials,subid)

	lst_del_nic = req.GET.getlist('abc')


	try:	
		lst = lst_del_nic[0].split(",")
		nic_res = network_client.network_interfaces.delete(lst[1],lst[0])
		nic_res.result()
	except Exception as e:
		return HttpResponse(e)
	else:
		return HttpResponse("nic successfully Deleted")


#this function is for deletion of vpn
def delvpn(req):

	mail = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])
	

	credentials = UserPassCredentials(mail,password)

	network_client = NetworkManagementClient(credentials,subid)

	lst_del_vpn = req.GET.getlist('abc')

	try:
		lst = lst_del_vpn[0].split(",")
		res = network_client.virtual_networks.delete(lst[1],lst[0])
		res.result()
	except Exception as e:
		return HttpResponse(e)
	else:
		return HttpResponse("Successfully Deleted!")

#this code is for deletion of public ip
def delpublic_ip(req):

	mail = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])
	

	credentials = UserPassCredentials(mail,password)

	network_client = NetworkManagementClient(credentials,subid)

	lst_del_pub_ip = req.GET.getlist('abc')

	try:
		lst = lst_del_pub_ip[0].split(",")
		res = network_client.public_ip_addresses.delete(lst[1],lst[0])
		res.result()
	except Exception as e:
		return HttpResponse(e)
	else:
		return HttpResponse("Successfully Deleted!")

def delnsg(req):

	mail = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])
	

	credentials = UserPassCredentials(mail,password)

	network_client = NetworkManagementClient(credentials,subid)

	lst_del_nsg = req.GET.getlist('abc')

	try:
		lst = lst_del_nsg[0].split(",")
		res = network_client.network_security_groups.delete(lst[1],lst[0])
		res.result()
	except Exception as e:
		return HttpResponse(e)
	else:
		return HttpResponse("Successfully Deleted!")

#code for deletion of VM
def delvm(req):

	mail = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])

	credentials = UserPassCredentials(mail,password)

	compute_client = ComputeManagementClient(credentials,subid)

	lst_del_vm = req.GET.getlist('abc')

	try:
		lst = lst_del_vm[0].split(",")
		res = compute_client.virtual_machines.delete(lst[1],lst[0])
		res.result()
	except Exception as e:
		return HttpResponse(e)
	else:
		return HttpResponse("Succesfully Deleted")

#code for deletion of ResourceGroup
def delres_grp(req):

	mail = req.session['email']
	password = req.session['azure_pwd']
	subid = str(req.session['subid'])

	credentials = UserPassCredentials(mail,password)

	resource_client = ResourceManagementClient(credentials,subid)

	lst_del_res_grp = req.GET.getlist('abc')

	try:
		
		res = resource_client.resource_groups.delete(lst_del_res_grp[0])
		res.result()
	except Exception as e:
		return HttpResponse(e)
	else:
		return HttpResponse("Succesfully Deleted")




#creation Code

#Give of VPN form
def vpn_form(req):
	return render(req,"form_vpn.html")

#creation of VPN
def vpn_creation(req):

	usr_mail = req.session['email']
	usr_pass = req.session['azure_pwd']
	subid = str(req.session['subid'])

	try:

		credentials = UserPassCredentials(usr_mail,usr_pass)
		network_client = NetworkManagementClient(credentials,subid)
		resource_client = ResourceManagementClient(credentials,subid)


		res_obj = resource_client.resource_groups.get(req.POST['drop1'])


		vpn_parameter = {
							'location':res_obj.location,
							'address_space':{ 'address_prefixes':[req.POST['vpn_address']] }


						}

		network_client.virtual_networks.create_or_update(req.POST['drop1'],req.POST['vpn_name'],vpn_parameter)

	except Exception as e:

		return HttpResponse(e)
	else:
		return HttpResponse("Successfully Created")	
		
#creation of vn with new resource group
def vpn_creation1(req):

	usr_mail = req.session['email']
	usr_pass = req.session['azure_pwd']
	subid = str(req.session['subid'])

	try:

		credentials = UserPassCredentials(usr_mail,usr_pass)
		network_client = NetworkManagementClient(credentials,subid)
		resource_client = ResourceManagementClient(credentials,subid)


		location = req.POST['drop_location']

		res_grp = req.POST['res_group_name']

		res_grp_parameter = {'location':location}

		resource_client.resource_groups.create_or_update(res_grp,res_grp_parameter)


		vpn_parameter = {
							'location':location,
							'address_space':{ 'address_prefixes':[req.POST['vpn_address']] }


						}

		network_client.virtual_networks.create_or_update(res_grp,req.POST['vpn_name'],vpn_parameter)

	except Exception as e:

		return HttpResponse(e)
	else:
		return HttpResponse("Successfully Created")	





#for form  of public ip
def public_ip_form(req):
	return render(req,'form_public_ip.html')

#for creation of public ip
def public_ip_creation(req):

	usr_mail = req.session['email']
	usr_pass = req.session['azure_pwd']
	subid = str(req.session['subid'])

	try:

		credentials = UserPassCredentials(usr_mail,usr_pass)
		network_client = NetworkManagementClient(credentials,subid)

		public_ip_parameter = {
							'location':req.POST['location'],
							'public_ip_allocation_method':'Static',
							'public_ip_address_version':'IPv4',
							'idle_timeout_in_minutes':4 #value must be in between 4 to 30


						}

		res = network_client.public_ip_addresses.create_or_update(req.POST['resgroup'],req.POST['public_ip_name'],public_ip_parameter)

		res1 = res.result()

	except Exception as e:

		return HttpResponse(e)
	else:
		return HttpResponse("Your public ip address is "+ str(res1.ip_address))	

#call form of subnet

def subnet_form(req):
	return render(req,'form_subnet.html')

#create subnet without nsg
def subnet_creation(req):

	usr_mail = req.session['email']
	usr_pass = req.session['azure_pwd']
	subid = str(req.session['subid'])

	try:

		credentials = UserPassCredentials(usr_mail,usr_pass)
		network_client = NetworkManagementClient(credentials,subid)

		subnet_parameter = {
							
							'address_prefix':req.POST['subnet_address']


						}

		res = network_client.subnets.create_or_update(req.POST['resgroup'],req.POST['vpn_name'],req.POST['subnet_name'],subnet_parameter)

		res1 = res.result()

	except Exception as e:
		return HttpResponse(e)
	else:
		return HttpResponse("succesfully created subnet")	


#call to form of nic
def nic_form(req):
	return render(req,'form_nic.html')

#creation of nic
def nic_creation(req):

	usr_mail = req.session['email']
	usr_pass = req.session['azure_pwd']
	subid = str(req.session['subid'])

	try:

		credentials = UserPassCredentials(usr_mail,usr_pass)
		network_client = NetworkManagementClient(credentials,subid)


		subnet = network_client.subnets.get(req.POST['resgroup'],req.POST['vpn_name'],req.POST['subnet_name'])

		public_ip_addresses = network_client.public_ip_addresses.get(req.POST['resgroup'],req.POST['public_ip_name'])

		nic_parameter = {
									'location':'eastus',
									'ip_configurations':[{'name':'IP_Config','subnet':{'id':subnet.id},'public_ip_address':{'id':public_ip_addresses.id}}]


								}

		res = network_client.network_interfaces.create_or_update(req.POST['resgroup'],req.POST['nic_name'],nic_parameter)
		res.result()
		

	except Exception as e:
		return HttpResponse(e)
	else:
		return HttpResponse("Successfully created")


#call form of storage account
def storage_acc_form(req):

	return render(req,'form_storage_acc.html')

#to create storage account

def storage_acc_creation(req):

	try:


		lst = req.POST.getlist('abc')

		

		credentials = jsonpickle.decode(req.session['credentials'])

		storage_acc_client = StorageManagementClient(credentials,str(req.session['subid']))

		availability = storage_acc_client.storage_accounts.check_name_availability(req.POST['storage_acc_name'])

		

		if availability.name_available: 

			

			storage_acc_parameter = { 'sku':{'name':lst[0]},'kind':'storage','location':req.POST['location'] }

			res = storage_acc_client.storage_accounts.create(req.POST['resgroup'],req.POST['storage_acc_name'],storage_acc_parameter)

			res.result()

	except Exception as e:
		return HttpResponse(e)
	else:
		return HttpResponse("Successfully created")


#frontend to all actions to network resources in azure

def network_content(req):

	return render(req,"network_content.html")

def test(req):
	return render(req,"test.html")

def test_back(req):

	lst = req.POST.getlist('abc')

	return HttpResponse(lst)



#just Test
from newapp.form import LoginForm

def login(req):

	username = "not logged in"

	if req.method == "POST":
		MyLoginForm = LoginForm(req.POST)

		if MyLoginForm.is_valid():

			username = MyLoginForm.cleanned_data['username']

			return HttpResponse(username)
	else:

		MyLoginForm = LoginForm()

	return render(req,"loggedin.html",{"username":username})


def network_content1(req):

	credentials = UserPassCredentials(req.session['email'],req.session['azure_pwd'])
	resource_client = ResourceManagementClient(credentials,str(req.session['subid']))

	lst = resource_client.resource_groups.list()

	lst_rg = []

	for item in lst:
		lst_rg.append(item.name)

	return render(req,"vertical_pilles.html",{"lst_rg":lst_rg})





