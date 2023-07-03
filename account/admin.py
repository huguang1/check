from django.contrib import admin

# Register your models here.

from account.models import MyUser, AdminPermission, AdminGroup, Banks, BankCard, Record


admin.site.register(MyUser)
admin.site.register(AdminPermission)
admin.site.register(AdminGroup)
admin.site.register(Banks)
admin.site.register(BankCard)
admin.site.register(Record)
