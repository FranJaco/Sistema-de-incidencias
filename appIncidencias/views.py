from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from .models import Department, Non_Tech_employee, Report, Tech_support_employee
import json
from datetime import timedelta, datetime
from django.utils.formats import date_format
from django.utils.dateparse import parse_date
from django.db.models.functions import Substr

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




def get_employees(request, department_id):
    # Obtener los empleados del departamento seleccionado
    employees = Non_Tech_employee.objects.filter(department_id=department_id)
    # Crear una lista de diccionarios con el ID y el nombre del empleado
    employee_data = [{
        'id': emp.id,
        'name': f"{emp.pile_name} {emp.sur_name}"
    } for emp in employees]

    return JsonResponse({'employees': employee_data})


def format_duration(duration):
    """Formatea una duración en un formato legible."""
    if duration is None:
        return "Sin resolver"  # Caso cuando no hay tiempo de resolución
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


@login_required
def home_view(request):
    return render(request, 'core/home.html')


@login_required
def view_by_department(request):
    departments = Department.objects.all()
    reports = Report.objects.all()

    # Si se pasa un parámetro 'department_id', filtramos los reportes
    department_id = request.GET.get('department_id')
    if department_id:
        reports = reports.filter(id__startswith=department_id)


    context = {
        'departments': departments,
    }



    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        report_list = []
        for report in reports:
            report_list.append({
                'id': report.id,
                'title': report.title,
                'creation_date': date_format(report.creation_date, format='N j, Y, P', use_l10n=True), 
                'non_tec_emp': f"{report.non_tec_emp.pile_name} {report.non_tec_emp.sur_name}",
                'resolution_time': format_duration(report.resolution_time),
                'tec_supp_emp': f"{report.tec_supp_emp.pile_name} {report.tec_supp_emp.sur_name}",  
                'summary': report.summary,
            })

        return JsonResponse({'reports': report_list})
    
    if request.method == 'POST' and 'delete_report_id' in request.POST:
        # Eliminar reporte
        report_id = request.POST['delete_report_id']
        report = get_object_or_404(Report, id=report_id)
        report.delete()
        return JsonResponse({'success': True})

    return render(request, 'core/home/viewByDepartment.html', context)


@login_required
def view_by_user(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_id = request.GET.get('user_id')
        if user_id:
            reports = Report.objects.filter(tec_supp_emp__id=user_id)  # Filtrar por usuario
            report_list = [
                {
                    'id': report.id,
                    'title': report.title,
                    'creation_date': date_format(report.creation_date, format='N j, Y, P', use_l10n=True), 
                    'non_tec_emp': f"{report.non_tec_emp.pile_name} {report.non_tec_emp.sur_name}",
                    'tec_supp_emp': f"{report.tec_supp_emp.pile_name} {report.tec_supp_emp.sur_name}",
                    'resolution_time': format_duration(report.resolution_time),
                    'summary': report.summary
                }
                for report in reports
            ]
            return JsonResponse({'reports': report_list})
    
    users = Tech_support_employee.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'core/home/viewByUser.html', context)


@login_required
def view_by_time(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        time_id = request.GET.get('time_id')

        # Definición de rangos ajustados
        time_ranges = {
            "1": (None, timedelta(minutes=1)),                
            "2": (timedelta(minutes=1), timedelta(minutes=6)), 
            "3": (timedelta(minutes=6), timedelta(minutes=11)),
            "4": (timedelta(minutes=11), timedelta(minutes=31)),
            "5": (timedelta(minutes=31), timedelta(minutes=61)),
            "6": (timedelta(minutes=61), timedelta(minutes=241)),
            "7": (timedelta(minutes=241), timedelta(minutes=481)),
            "8": (timedelta(minutes=481), None),              
        }

        # Verificar si el rango solicitado es válido
        if time_id not in time_ranges:
            return JsonResponse({"error": "Tiempo no válido"}, status=400)

        # Obtener los límites inferior y superior del rango
        lower_limit, upper_limit = time_ranges[time_id]

        # Filtrar los reportes dentro del rango especificado
        if lower_limit is None:
            reports = Report.objects.filter(resolution_time__lt=upper_limit)
        elif upper_limit is None:
            reports = Report.objects.filter(resolution_time__gte=lower_limit)
        else:
            reports = Report.objects.filter(resolution_time__gte=lower_limit, resolution_time__lt=upper_limit)

        # Serializar datos para el frontend
        report_list = [
            {
                'id': report.id,
                'title': report.title,
                'creation_date': date_format(report.creation_date, format='N j, Y, P', use_l10n=True),
                'non_tec_emp': f"{report.non_tec_emp.pile_name} {report.non_tec_emp.sur_name}",
                'tec_supp_emp': f"{report.tec_supp_emp.pile_name} {report.tec_supp_emp.sur_name}",
                'resolution_time': format_duration(report.resolution_time),
                'summary': report.summary,
            }
            for report in reports
        ]

        return JsonResponse({'reports': report_list})

    context = {}
    return render(request, 'core/home/viewByTime.html', context)

@login_required
def view_by_employee(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        employee_id = request.GET.get('employee_id')
        if employee_id:
            reports = Report.objects.filter(non_tec_emp=employee_id)  # Filtrar por usuario
            report_list = [
                {
                    'id': report.id,
                    'title': report.title,
                    'creation_date': date_format(report.creation_date, format='N j, Y, P', use_l10n=True), 
                    'non_tec_emp': f"{report.non_tec_emp.pile_name} {report.non_tec_emp.sur_name}",
                    'tec_supp_emp': f"{report.tec_supp_emp.pile_name} {report.tec_supp_emp.sur_name}",
                    'resolution_time': format_duration(report.resolution_time),
                    'summary': report.summary
                }
                for report in reports
            ]
            return JsonResponse({'reports': report_list})
    
    departments = Department.objects.all()
    employees = Non_Tech_employee.objects.all()


    context = {
        'employees': employees,
        'departments': departments
    }
    return render(request, 'core/home/viewByEmployee.html', context)

@login_required
def view_by_date(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        selected_date = request.GET.get('date_id')  # Obtener la fecha seleccionada

        if not selected_date:
            return JsonResponse({"error": "No se proporcionó una fecha"}, status=400)

        # Usar parse_date para convertir la fecha en un objeto de tipo datetime.date
        date_filter = parse_date(selected_date)

        if not date_filter:
            return JsonResponse({"error": "Fecha inválida"}, status=400)

        # Filtrar los reportes por la fecha de creación
        reports = Report.objects.filter(creation_date__date=date_filter)

        # Serializar los datos para el frontend
        report_list = [
            {
                'id': report.id,
                'title': report.title,
                'creation_date': date_format(report.creation_date, format='N j, Y, P', use_l10n=True),
                'non_tec_emp': f"{report.non_tec_emp.pile_name} {report.non_tec_emp.sur_name}",
                'tec_supp_emp': f"{report.tec_supp_emp.pile_name} {report.tec_supp_emp.sur_name}",
                'resolution_time': format_duration(report.resolution_time),
                'summary': report.summary,
            }
            for report in reports
        ]

        return JsonResponse({'reports': report_list})
    context = {}
    # Renderizar la plantilla en caso de solicitud GET estándar
    return render(request, 'core/home/viewByDate.html', context)


@login_required
def view_by_search(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        title_id = request.GET.get('title_id')
        if title_id:
            reports = Report.objects.filter(title__icontains=title_id)  # Filtrar por usuario
            report_list = [
                {
                    'id': report.id,
                    'title': report.title,
                    'creation_date': date_format(report.creation_date, format='N j, Y, P', use_l10n=True), 
                    'non_tec_emp': f"{report.non_tec_emp.pile_name} {report.non_tec_emp.sur_name}",
                    'tec_supp_emp': f"{report.tec_supp_emp.pile_name} {report.tec_supp_emp.sur_name}",
                    'resolution_time': format_duration(report.resolution_time),
                    'summary': report.summary
                }
                for report in reports
            ]
            return JsonResponse({'reports': report_list})
    context = {}
    return render(request, 'core/home/viewBySearch.html', context)

@login_required
def add_reports(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        title = data.get('title')
        summary = data.get('summary')
        department_id = data.get('department_id')
        employee_id = data.get('employee_id')
        time_estimate = data.get('time')  # Capturar el tiempo estimado

        if not title or not summary or not department_id or not employee_id or not time_estimate:
            return JsonResponse({'success': False, 'error': 'Todos los campos son necesarios.'})

        # Mapeo de las opciones de tiempo estimado a minutos
        time_map = {
            "1": 1,     
            "2": 5,   
            "3": 10,    
            "4": 30,  
            "5": 60,  
            "6": 240,  
            "7": 480,  
            "8": 481,   
        }

        # Validar que el valor esté dentro del mapa
        if time_estimate not in time_map:
            return JsonResponse({'success': False, 'error': 'Tiempo estimado inválido.'})

        # Obtener la duración en minutos y convertirla a timedelta
        resolution_time_minutes = time_map[time_estimate]
        resolution_time = timedelta(minutes=resolution_time_minutes)

        try:
            # Crear el reporte con el tiempo estimado de resolución
            report = Report(
                title=title,
                summary=summary,
                tec_supp_emp=request.user,
                non_tec_emp_id=employee_id,
                resolution_time=resolution_time
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
