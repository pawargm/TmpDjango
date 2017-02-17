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
]