from django.db import models
from django.utils import timezone

class Device(models.Model):
    id     = models.AutoField(primary_key=True, unique=True, editable=False)
    esp_id = models.CharField(max_length=12, default='')
    area = models.IntegerField(default=0)
    node = models.CharField(max_length=50, default='')
    variables = models.JSONField(default={})
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    master = models.BooleanField(default=False)

    def __str__(self):
        return f'Dispositivo {self.id} - {self.esp_id}'
    