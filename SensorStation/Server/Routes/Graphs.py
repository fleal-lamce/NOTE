from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from django.http import HttpResponse
import json, orjson
import sqlite3
import pandas as pd


def getGraph(key):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    table  = 'Logs_log'
    df = pd.read_sql_query(f'SELECT * FROM {table} ORDER BY id DESC LIMIT 15', conn)
    print(df.head())
    return {key: str(tables)}

@csrf_exempt
@action(detail=False, methods=['post'], url_path='replace')
def onGraphRequest(request):
    data = json.loads(request.body)
    key  = data.get('key')
    return HttpResponse(orjson.dumps(getGraph(key)), content_type='application/json')

