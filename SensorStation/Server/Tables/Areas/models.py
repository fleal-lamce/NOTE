from django.db import models
from django.utils import timezone

class Area(models.Model):
    id = models.AutoField(primary_key=True, unique=True, editable=False)
    value = models.IntegerField(default=0)
    label = models.CharField(max_length=30, default='GRVA')
    
    def __str__(self):
        return f'Area {self.value} - {self.label}'
    