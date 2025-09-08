import orjson
from django.apps import apps
from django.db import connection
from Utils.functions import sendEvent
from Tables.Logs.models import Log
from Tables.Areas.models import Area


class API:
    url = 'http://0.0.0.0:8000/'

    def getModel(self, name):
        if name == 'logs':
            return Log
        
        if name == 'areas':
            return Area
        
        return None

    def columns(self, table):
        model  = self.getModel(table)
        fields = model._meta.fields
        return {field.column for field in fields if not (field.auto_created and not field.concrete)}

    def get(self, table, limit=None):
        model = self.getModel(table)

        if model is None:
            return orjson.dumps([])

        table = model._meta.db_table
        
        sql    = f"SELECT * FROM {table} "
        params = []

        if limit:
            sql += ("LIMIT %s" if limit > 0 else 'ORDER BY id DESC LIMIT %s')
            params.append(abs(limit))

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            cols = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        if limit and limit < 0: 
            rows = rows[::-1] 
    
        return orjson.dumps({'status': 'success', 'data': [dict(zip(cols, row)) for row in rows]})

    def add(self, table, data):
        model = self.getModel(table)
        
        if model is None:
            return orjson.dumps({'status': 'error', 'data': 'table not found'})

        try:
            if isinstance(data, str):
                data = orjson.loads(data.strip())
            
            target = {key: value for key, value in data.items() if key in self.columns(table)}
            print('to insert: ', data)

            instance = model.objects.create(**target)
            instance.save()
        except Exception as error:
            sendEvent('error', error)
            return orjson.dumps({'status': 'error', 'data': str(error)})


        return orjson.dumps({'status': 'success', 'data': 'data inserted'})


api = API()
