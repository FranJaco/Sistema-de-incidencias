from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from .models import Department, Non_Tech_employee, Report, Tech_support_employee
import json

def admin_required(user):
    return user.is_authenticated and user.is_admin

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


@login_required
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
    if request.method == 'POST':
        data = json.loads(request.body)

        title = data.get('title')
        summary = data.get('summary')
        department_id = data.get('department_id')
        employee_id = data.get('employee_id')

        if not title or not summary or not department_id or not employee_id:
            return JsonResponse({'success': False, 'error': 'Todos los campos son necesarios.'})

        try:
            # Crear el reporte con el usuario autenticado
            report = Report(
                title=title,
                summary=summary,
                tec_supp_emp=request.user,  # Usuario actual
                non_tec_emp_id=employee_id
            )
            report.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    # Renderizar formulario en GET
    context = {
        'departments': Department.objects.all(),
        'employees': Non_Tech_employee.objects.all(),
    }
    return render(request, 'core/addReports.html', context)

@user_passes_test(admin_required)
@login_required
def user_managment(request):
    if request.method == 'POST':
        try:
            # Cargar los datos del cuerpo de la solicitud
            data = json.loads(request.body)
            
            # Verificar la acción
            if data.get('action') == "create_new_user":
                # Obtener y validar datos
                name = data.get('name')
                lastname = data.get('lName')
                username = data.get('uName')
                password = data.get('password')
                isAdmin = str(data.get('isAdmin', False)).lower() in ['true', '1']

                if not name or not lastname or not username or not password:
                    return JsonResponse({'success': False, 'error': 'Todos los campos son necesarios.'})

                if len(password) < 8:
                    return JsonResponse({'success': False, 'error': 'La contraseña debe tener al menos 8 caracteres.'})

                if not username.isalnum():
                    return JsonResponse({'success': False, 'error': 'El nombre de usuario solo puede contener letras y números.'})

                # Crear usuario utilizando el manager
                user = Tech_support_employee.objects.create_user(
                    pile_name=name,
                    sur_name=lastname,
                    username=username,
                    password=password
                )
                user.is_admin = isAdmin
                user.save()

                return JsonResponse({'success': True})
            
            elif data.get('action') == "delete_user":
                user_id = data.get('userID')  # Obtener el id del usuario a eliminar
                if not user_id:
                    return JsonResponse({'success': False, 'error': 'Se debe proporcionar un ID de usuario.'})

                # Verificar si el usuario existe
                user = Tech_support_employee.objects.filter(id=user_id).first()
                if not user:
                    return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'})

                # Eliminar el usuario
                user.delete()

                return JsonResponse({'success': True, 'message': 'Usuario eliminado exitosamente.'})

        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'El nombre de usuario ya existe.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Datos inválidos en la solicitud.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error desconocido: {str(e)}'})
        


    # Lógica para GET
    users_list = Tech_support_employee.objects.all()
    paginator = Paginator(users_list, 10)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    context = {
        'users': users,
    }
    return render(request, 'core/userManagment.html', context)



@login_required
def view_reports(request):
    if request.method == 'POST' and 'delete_report_id' in request.POST:
        # Eliminar reporte
        report_id = request.POST['delete_report_id']
        report = get_object_or_404(Report, id=report_id)
        report.delete()
        return JsonResponse({'success': True})

    reports = Report.objects.all()

    context = {
        'reports': reports,
    }

    return render (request, 'core/viewReports.html', context)
