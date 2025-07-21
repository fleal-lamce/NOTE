from django.views.decorators.csrf import csrf_exempt
from django.contrib import admin
from django.urls import path
from rest_framework.decorators import action
from django.http import HttpResponse
from Utils.API import api
import json, orjson

from Routes.Graphs import *


@csrf_exempt
@action(detail=False, methods=['get'], url_path='replace')
def onCheckRequest(request):
    print(request.body)
    return HttpResponse(orjson.dumps({'status': 'success', 'data': 'OK'}), content_type='application/json')

@csrf_exempt
@action(detail=False, methods=['post'], url_path='replace')
def onRowsRequest(request):
    data  = json.loads(request.body)
    table = data.get('table')
    limit = data.get('limit')
    return HttpResponse(api.get(table, limit), content_type='application/json')

@csrf_exempt
@action(detail=False, methods=['post'], url_path='replace')
def onAddRequest(request):
    data  = json.loads(request.body)
    table = data.get('table')
    data  = data.get('data')
    return HttpResponse(api.add(table, data), content_type='application/json')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/check/', onCheckRequest),
    path('api/rows/', onRowsRequest),
    path('api/add/', onAddRequest),
    path('api/graph/', onGraphRequest)
]
