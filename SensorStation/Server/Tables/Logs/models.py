from django.db import models
from django.utils import timezone


class Log(models.Model):
    id = models.AutoField(primary_key=True, unique=True, editable=False)
    esp_id = models.CharField(max_length=12, default='')
    area   = models.IntegerField(default=0)
    data   = models.JSONField(default={}) 
    timestamp = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f'Log {self.id} | ESP {self.esp_id} | {timezone.localtime(self.timestamp):%Y-%m-%d %H:%M:%S}'
    