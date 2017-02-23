from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

urlpatterns = [

		url(r'^date/$',views.current_datetime, name = 'cuurent_datetime'),
		url(r'^search-form/$',views.search_form, name = 'search_form'),
		url(r'^search/',views.authenticate, name = 'authenticate'),
		url(r'^lst_rg/',views.list_resource, name = 'list_resource'),
		url(r'^check_netrc/',views.check_netrc,name = 'check_netrc'),
		url(r'^login_acc/',views.login_acc,name = 'login_acc'),
		url(r'^azure_res/',views.azure_res,name = 'azure_res'),
		url(r'^vm_lst/',views.lst_vm,name = 'lst_vm'),
		url(r'^str_acc_lst/',views.lst_storage_acc,name ='lst_storage_acc'),
		url(r'^lst_vpn/',views.lst_vpn, name = 'lst_vpn'),
		url(r'^lst_pub_ips/',views.lst_pub_ips,name = 'lst_pub_ips'),
		url(r'^lst_nic/',views.lst_nic,name = 'lst_nic'),
		url(r'^lst_nsg/',views.lst_nsg,name = 'lst_nsg'),
		url(r'^lst_res_group/',views.lst_rg,name = 'lst_rg'),
		url(r'^call_form/',views.call_form,name = 'call_form'),
		url(r'^backj/',views.backj,name = 'backj')
]