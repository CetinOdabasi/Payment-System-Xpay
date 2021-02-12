from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm, XpayAccountForm
from .models import MyUser, XpayAccount, Currency_files,Country_files
from django.contrib.auth import get_user_model

MyUser = get_user_model()


class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm


    list_display = ('email', 'first_name', 'last_name', 'phone_number',
                    'country', 'last_login', 'admin', 'active', 'date_joined', 'staff')
    list_filter = ('admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('is_admin', 'is_staff','is_active')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'country')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()



admin.site.register(MyUser, UserAdmin)
admin.site.register(XpayAccount)
admin.site.register(Country_files)
admin.site.register(Currency_files)

admin.site.unregister(Group)
