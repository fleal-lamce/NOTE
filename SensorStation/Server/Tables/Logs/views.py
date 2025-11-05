from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from django.http import HttpResponse
from Utils.API import api
from Tables.Devices.models import Device
import json, ast


@csrf_exempt
@action(detail=False, methods=['post'], url_path='replace')
def onAddLogRequest(request):
    try:
        data = json.loads(request.body)
        esp_id = data['esp_id']
        variables = ast.literal_eval(data['variables'])
    except Exception as error:
        return api.send('success', f'not inserted: {error}')
    
    if esp_id is None or variables is None:
        return api.send('error', 'important keys missing')

    row  = Device.objects.filter(esp_id=esp_id).values('variables').first()
    data = {'esp_id': esp_id, 'data': {}}

    if not row:
        return api.send('error', 'variables error')

    for i, var in enumerate(row['variables']):
        data['data'][var] = variables[i]

    print(data)
    return HttpResponse(api.add('logs', data))
