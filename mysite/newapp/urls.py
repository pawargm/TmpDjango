from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

urlpatterns = [

		url(r'^date/$',views.current_datetime, name = 'cuurent_datetime'),
		url(r'^search-form/$',views.search_form, name = 'search_form'),
		url(r'^search/',views.authenticate, name = 'authenticate'),
		url(r'^lst_rg/',views.list_resource, name = 'list_resource'),
		url(r'^check_netrc/',views.check_netrc,name = 'check_netrc'),
		url(r'^index/',views.index,name = 'index'),
		url(r'^azure_res/',views.azure_res,name = 'azure_res'),
		url(r'^vm_lst/',views.lst_vm,name = 'lst_vm'),
		url(r'^str_acc_lst/',views.lst_storage_acc,name ='lst_storage_acc'),
		url(r'^lst_vpn/',views.lst_vpn, name = 'lst_vpn'),
		url(r'^lst_pub_ips/',views.lst_pub_ips,name = 'lst_pub_ips'),
		url(r'^lst_nic/',views.lst_nic,name = 'lst_nic'),
		url(r'^lst_nsg/',views.lst_nsg,name = 'lst_nsg'),
		url(r'^lst_res_group/',views.lst_rg,name = 'lst_rg'),
		url(r'^call_form/',views.call_form,name = 'call_form'),
		url(r'^backj/',views.backj,name = 'backj'),
		url(r'^signup_acc/',views.signup_acc,name = 'signup_acc'),
		url(r'^login_acc/',views.login_acc,name = 'login_acc'),

		#to make main account
		url(r'^make_account/',views.make_account,name = 'make_account'),


		url(r'^check_account/',views.check_account,name='check_account'),
		url(r'^login_to_azure/',views.login_to_azure,name='login_to_azure'),
		url(r'^login_to_azure_account/',views.login_to_azure_account,name='login_to_azure_account'),

		url(r'^login_azure_only_pass/',views.login_azure_only_pass,name='login_azure_only_pass'),
		url(r'^logout_main_acc/',views.logout_main_acc,name='logout_main_acc'),
		url(r'^output/',views.output,name='output'),
		url(r'^output1/',views.output1,name='output1'),	
		url(r'^delstorage/',views.delstorage,name='delstorage'),
		url(r'^delnic/',views.delnic,name = 'delnic'),
		url(r'^delvpn/',views.delvpn,name = 'delvpn'),
		url(r'^delpublic_ip/',views.delpublic_ip,name='delpublic_ip'),
		url(r'^delnsg/',views.delnsg,name='delnsg'),
		url(r'^delvm/',views.delvm,name='delvm'),
		url(r'^vpn_form/',views.vpn_form,name='vpn_form'),
		url(r'^vpn_creation/',views.vpn_creation,name='vpn_creation'),
		url(r'^vpn_creation1/',views.vpn_creation1,name='vpn_creation1'),
		url(r'^public_ip_form/',views.public_ip_form,name='public_ip_form'),
		url(r'^public_ip_creation/',views.public_ip_creation,name='public_ip_creation'),
		url(r'^subnet_form/',views.subnet_form,name='subnet_form'),
		url(r'^subnet_creation',views.subnet_creation,name='subnet_creation'),
		url(r'^nic_form/',views.nic_form,name='nic_form'),
		url(r'^nic_creation/',views.nic_creation,name='nic_creation'),
		url(r'^storage_acc_form/',views.storage_acc_form,name='storage_acc_form'),
		url(r'^storage_acc_creation/',views.storage_acc_creation,name='storage_acc_creation'),
		url(r'^network_content/',views.network_content,name='network_content'),

		url(r'^test/',views.test,name='test'),
		url(r'^test_back/',views.test_back,name='test_back'),
		url(r'^connection/',TemplateView.as_view(template_name='login.html')),
		url(r'^login/', views.login, name = 'login'),
		url(r'^network_content1/',views.network_content1,name='network_content1'),
		

]