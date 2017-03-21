from django.contrib import admin

# Register your models here.

from .models import Account
from .models import Azure_Account

admin.site.register(Account)
admin.site.register(Azure_Account)