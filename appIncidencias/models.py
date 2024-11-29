from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from datetime import datetime


class Department(models.Model):
    dep_name = models.CharField(max_length=30, unique=True)
    id = models.CharField(max_length=20, primary_key=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            # Generar un identificador único basado en el conteo de objetos
            ultimo_id = Department.objects.count() + 1
            self.id = f"DEP-{ultimo_id:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.dep_name


class TechSupportEmployeeManager(BaseUserManager):
    def create_user(self, pile_name, sur_name, username, password=None):
        if not username:
            raise ValueError("El usuario debe tener un nombre de usuario")
        user = self.model(pile_name=pile_name, sur_name=sur_name, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, pile_name, sur_name, username, password=None):
        user = self.create_user(pile_name, sur_name, username, password)
        user.is_admin = True 
        user.is_superuser =True
        user.save(using=self._db)
        return user


class Tech_support_employee(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    pile_name = models.CharField(max_length=30)
    sur_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    
    id = models.CharField(max_length=20, primary_key=True, editable=True)

    def save(self, *args, **kwargs):
        if not self.id:
            # Generar un identificador único basado en el conteo de objetos
            ultimo_id = Tech_support_employee.objects.count() + 1
            self.id = f"USER-{ultimo_id:02d}"
        super().save(*args, **kwargs)

    objects = TechSupportEmployeeManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['pile_name', 'sur_name']

    def __str__(self):
        return f"{self.pile_name} {self.sur_name}"

    @property
    def is_staff(self):
        return self.is_admin


class Non_Tech_employee(models.Model):
    pile_name = models.CharField(max_length=30)
    sur_name = models.CharField(max_length=30)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    id = models.CharField(max_length=20, primary_key=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            # Obtener el último empleado no técnico del mismo departamento
            last_employee = Non_Tech_employee.objects.filter(department=self.department).order_by('-id').first()
            
            # Generar un identificador basado en el departamento y el conteo de empleados
            department_code = self.department.id  # Usamos el ID del departamento
            last_id_number = int(last_employee.id.split('-')[1]) if last_employee else 0
            self.id = f"{department_code}-EMP-{last_id_number + 1:02d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pile_name} {self.sur_name}"


class Report(models.Model):
    title = models.CharField(max_length=50)
    summary = models.TextField()
    creation_date = models.DateTimeField(editable=False, default=datetime.now)
    tec_supp_emp = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    non_tec_emp = models.ForeignKey(Non_Tech_employee, on_delete=models.CASCADE)

    id = models.CharField(max_length=50, primary_key=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:

            if not self.creation_date:
                self.creation_date = datetime.now()

            # Obtener el id del departamento al que pertenece el reporte
            department_id = self.non_tec_emp.department.id  # Suponiendo que el reporte tiene un Non_Tech_employee asignado

            # Formatear la fecha de creación (por ejemplo: "2024-11-28")
            creation_date_str = self.creation_date.strftime('%Y-%m-%d')

            # Generar el número secuencial para el reporte del mismo departamento y fecha
            last_report = Report.objects.filter(
                non_tec_emp__department=self.non_tec_emp.department,
                creation_date__date=self.creation_date.date()
            ).order_by('-id').first()

            last_number = 0

            if last_report:
                try:
                    last_number = int(last_report.id.split('-')[-1])
                except ValueError:
                    last_number = 0  # Manejar IDs mal formateados

            # Crear el nuevo id en el formato "DEP-YYYY-MM-DD-XX"
            self.id = f"{department_id}-{creation_date_str}-{last_number + 1:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
