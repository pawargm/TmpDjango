import os
import netrc
import datetime
from haikunator import Haikunator
from newapp.form import LoginForm
from django.shortcuts import render
from django.http import HttpResponse
from azure.mgmt.resource import ResourceManagementClient
from azure.common.credentials import UserPassCredentials
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient




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



def call_form(req):

	return render(req,'form.html')

def backj(req):

	if os.path.isfile("netrc"):
		info = netrc.netrc("netrc")
		#append Username to machine here we appaends just email 
		machine = "portal.azure.com"+"Gopal.Pawar@veritas.com"#We have to take username from database
		email = info.authenticators(machine)[0]
		password = info.authenticators(machine)[2]
		subid = "c721e2fd-94b3-4155-952e-60ba88bc1f6a"

		haikunator = Haikunator()

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










