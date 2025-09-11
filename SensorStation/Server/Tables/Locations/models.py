from django.db import models


class Location(models.Model):
    id  = models.AutoField(primary_key=True, unique=True, editable=False)
    lat = models.FloatField(default=0)
    lng = models.FloatField(default=0)
    label = models.CharField(max_length=50, default='Lamce COPPE/UFRJ')
    value = models.CharField(max_length=10, default='')

    def __str__(self):
        return f'{self.label}'
