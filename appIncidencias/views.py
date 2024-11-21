from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Department, Non_Tech_employee, Report
import json

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse('home')) 
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'core/login.html')

# def get_hour(request):
 #   time_now= datetime.now().strftime('%H:%M:%S')
  #  return JsonResponse({'hour': time_now}) 

def get_employees(request, department_id):
    # Obtener los empleados del departamento seleccionado
    employees = Non_Tech_employee.objects.filter(department_id=department_id)
    # Crear una lista de diccionarios con el ID y el nombre del empleado
    employee_data = [{
        'id': emp.id,
        'name': f"{emp.pile_name} {emp.sur_name}"
    } for emp in employees]

    return JsonResponse({'employees': employee_data})


def home_view(request):
    return render(request, 'core/home.html')

@login_required
def add_reports(request):
    departments = Department.objects.all()
    nte = Non_Tech_employee.objects.all()

    if request.method == 'POST':
        # Si el formulario fue enviado, manejar la creación del reporte
        data = json.loads(request.body)  # Recibimos los datos en formato JSON

        title = data.get('title')
        summary = data.get('summary')
        department_id = data.get('department_id')
        employee_id = data.get('employee_id')

        if not title or not summary or not department_id or not employee_id:
            return JsonResponse({'success': False, 'error': 'Todos los campos son necesarios.'})

        # Crear el reporte en la base de datos
        try:
            report = Report.objects.create(
                title=title,
                summary=summary,
                tec_supp_emp=request.user,  # El usuario autenticado es el que crea el reporte
                non_tec_emp_id=employee_id
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    context = {
        'departments': departments,
        'employees': nte,
    }
    return render (request, 'core/addReports.html', context)

def user_managment(request):
    return render (request, 'core/userManagment.html')

def view_reports(request):
    return render (request, 'core/viewReports.html')
