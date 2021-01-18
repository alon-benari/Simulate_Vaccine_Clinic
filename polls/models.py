from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 


class SimParamsModel (models.Model):
    admin_stations = models.SmallIntegerField( null=False, validators=[MinValueValidator(1), MaxValueValidator(100)])
    admin_low = models.PositiveSmallIntegerField(null=False, validators=[MinValueValidator(1), MaxValueValidator(100)])
    admin_hi = models.PositiveSmallIntegerField(null=False, validators=[MinValueValidator(1), MaxValueValidator(100)])

    def __str__(self):
        return self.title
# Create your models here.
