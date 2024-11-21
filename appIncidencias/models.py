from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings 

# Create your models here.
class Department(models.Model):
    dep_name            = models.CharField(max_length=30)
    amount_of_employees = models.PositiveIntegerField()

    def __str__(self):
        return self.dep_name
    
#class Tech_support_employee(models.Model):
#    pile_name = models.CharField(max_length=30)
#    sur_name  = models.CharField(max_length=30)
#    
#    def __str__(self):
#        return f"{self.pile_name} {self.sur_name}"

# 1. Crear el Manager personalizado
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
        user.save(using=self._db)
        return user

# 2. Crear el modelo Tech_support_employee como modelo de usuario
class Tech_support_employee(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True, default = 'user1')
    pile_name = models.CharField(max_length=30)
    sur_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    password = models.CharField(max_length=128, default='123')

    objects = TechSupportEmployeeManager()

    USERNAME_FIELD = 'username'  # Este es el campo que usaremos para autenticarnos
    REQUIRED_FIELDS = ['pile_name', 'sur_name']  # Campos obligatorios al crear un usuario

    def __str__(self):
        return f"{self.pile_name} {self.sur_name}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
    
    

class Non_Tech_employee(models.Model):
    pile_name   = models.CharField(max_length=30)
    sur_name    = models.CharField(max_length=30)
    department  = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pile_name} {self.sur_name}"
    

class Report(models.Model):
    title           = models.CharField(max_length=50)
    summary         = models.TextField()
    creation_date   = models.DateTimeField(auto_now_add=True)
    tec_supp_emp = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    non_tec_emp     = models.ForeignKey(Non_Tech_employee, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title


class Dep_Chief(models.Model):
    pile_name   = models.CharField(max_length=30)
    sur_name    = models.CharField(max_length=30)

    department  = models.OneToOneField(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pile_name} {self.sur_name}"
