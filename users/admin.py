from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('userId', 'email', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('userId', 'email')
    ordering = ('userId',)
    readonly_fields = ('last_login', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('userId', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new user
            obj.set_password(form.cleaned_data.get('password'))
        elif 'password' in form.changed_data:
            obj.set_password(form.cleaned_data.get('password'))
        super().save_model(request, obj, form, change)
