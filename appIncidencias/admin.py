from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import  *
# Register your models here.

class TechSupportEmployeeAdmin(UserAdmin):
    model = Tech_support_employee
    # Configuración de campos para mostrar en el panel de administración
    list_display = ('username', 'pile_name', 'sur_name', 'is_admin', 'is_active')
    list_filter = ('is_admin', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('pile_name', 'sur_name')}),
        ('Permisos', {'fields': ('is_admin', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'pile_name', 'sur_name', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'pile_name', 'sur_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')

admin.site.register(Department)

admin.site.register(Tech_support_employee, TechSupportEmployeeAdmin)

admin.site.register(Non_Tech_employee)

admin.site.register(Report)
