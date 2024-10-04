from django.db import models

# Create your models here.
class Department(models.Model):
    dep_name            = models.CharField(max_length=30)
    amount_of_employees = models.PositiveIntegerField()

    def __str__(self):
        return self.dep_name
    
class Tech_support_employee(models.Model):
    pile_name = models.CharField(max_length=30)
    sur_name  = models.CharField(max_length=30)
    
    def __str__(self):
        return f"{self.pile_name} {self.sur_name}"
    
    

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
    tec_supp_emp    = models.ForeignKey(Tech_support_employee, on_delete=models.CASCADE)
    non_tec_emp     = models.ForeignKey(Non_Tech_employee, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title


class Dep_Chief(models.Model):
    pile_name   = models.CharField(max_length=30)
    sur_name    = models.CharField(max_length=30)

    department  = models.OneToOneField(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pile_name} {self.sur_name}"
