"""
URL configuration for sistema_incidencias project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import login_view, home_view, add_reports, view_reports, user_managment, get_employees,view_by_department, view_by_user, view_by_time, view_by_employee, view_by_date, view_by_search

urlpatterns = [
    path('', login_view, name='login'),
    path('home/', home_view, name='home'),
    path('addReports/', add_reports,  name='addReports'),
    path('viewReports/', view_reports, name='viewReports'),
    path('userManagment/', user_managment, name='userManagment'),
    path('get_employees/<str:department_id>/', get_employees, name='get_employees'),
    path('core/home/viewByDepartment', view_by_department, name='viewByDepartment'), 
    path('core/home/viewByUser', view_by_user, name='viewByUser'), 
    path('core/home/viewByTime', view_by_time, name='viewByTime'), 
    path('core/home/viewByEmployee', view_by_employee, name='viewByEmployee'), 
    path('core/home/viewByDate', view_by_date, name='viewByDate'), 
    path('core/home/viewBySearch', view_by_search, name='viewBySearch'),
    path('logout/', LogoutView.as_view(), name='logout'),
]