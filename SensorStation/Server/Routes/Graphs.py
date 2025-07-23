from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from django.http import HttpResponse
import json, orjson
import sqlite3, ast
import pandas as pd


def getGraph(key):
    conn   = sqlite3.connect('db.sqlite3')
    slaves = pd.read_sql_query(f'SELECT * FROM Devices_device WHERE master=false', conn).esp_id.tolist()
    query  = f"SELECT * FROM Logs_log WHERE esp_id IN ({', '.join(['?'] * len(slaves))}) ORDER BY id DESC LIMIT 15"
    df     = pd.read_sql_query(query, conn, params=slaves)

    return {
        'status': 'success',
        'data': [data.get(key) for data in df.data.apply(ast.literal_eval) if data.get(key) is not None]
    }


@csrf_exempt
@action(detail=False, methods=['post'], url_path='replace')
def onGraphRequest(request):
    data = json.loads(request.body)
    key  = data.get('key')
    return HttpResponse(orjson.dumps(getGraph(key)), content_type='application/json')

