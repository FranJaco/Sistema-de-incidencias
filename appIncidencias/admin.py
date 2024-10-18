from django.contrib import admin
from .models import  *
# Register your models here.

admin.site.register(Department)

admin.site.register(Tech_support_employee)

admin.site.register(Non_Tech_employee)

admin.site.register(Report)

admin.site.register(Dep_Chief)