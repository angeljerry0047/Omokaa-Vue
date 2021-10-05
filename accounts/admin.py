from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import Account,Feedback,HelpMessage


class AccountAdmin(UserAdmin):
    list_display = ('name', 'username', 'email', 'country_code', 'phone', 'profile_pic', 'date_joined', 'last_login', 'is_admin', 'is_active')
    search_fields = ('name', 'username', 'email', 'phone',)
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined', )
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    list_per_page = 10


admin.site.register(Account, AccountAdmin)
admin.site.register(Feedback)
admin.site.register(HelpMessage)
