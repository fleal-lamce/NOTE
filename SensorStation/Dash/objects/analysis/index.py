import pandas as pd
import sqlite3, ast
from datetime import datetime
from zoneinfo import ZoneInfo


class Analysis:
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.database  = pd.DataFrame()
        self.df        = pd.DataFrame() 
        self.variables = [{'label': 'Temperatura', 'value': 'temperature'}, {'label': 'Humidity', 'value': 'humidity'}]
        self.devices = []
        self.areas   = []
        self.device = 'all'
        self.area   = 'all'

    def download(self):
        conn = sqlite3.connect('../Server/db.sqlite3')
        self.database = pd.read_sql_query('SELECT * FROM (SELECT * FROM Logs_log ORDER BY id DESC LIMIT 15000) AS subquery_alias ORDER BY id ASC;', conn)

        self.database['data'] = self.database.data.apply(ast.literal_eval)
        self.database['time'] = pd.to_datetime(self.database.timestamp, errors='coerce')

    def update(self):
        self.df = pd.concat([
            self.database.time,
            self.database.esp_id,
            self.database.area,
            pd.json_normalize(self.database.data)
        ], axis=1)

        self.devices = [{'label': 'todos', 'value': 'all'}] + [{'label': id, 'value': id} for id in self.database.esp_id.unique()]
        self.areas   = [{'label': 'todos', 'value': 'all'}] + [{'label': area, 'value': area} for area in self.database.area.unique()]

        if self.area != 'all':
            self.df = self.df.loc[self.df.area == self.area]

        if self.device != 'all':
            self.df = self.df.loc[self.df.esp_id == self.device]

        self.curr_time = datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')
        self.timestamp = self.getLastVar('time').strftime('%d/%m/%Y %H:%M:%S') if self.getLastVar('time') else 'N/A'
        self.temperature = self.getLastVar('temperature', number=True)
        self.humidity = self.getLastVar('humidity', number=True)
        self.pressure = self.getLastVar('pressure', number=True)
        self.wind = self.getLastVar('wind', number=True)

        if len(self.df) > 150:
            self.df = self.df.tail(150)

    def getLastVar(self, key, number=False):
        s = self.df.get(key)
        if s is None:
            return None
        
        s = s.dropna()
        if number:
            return float(s.iloc[-1]) if not s.empty else -1

        return s.iloc[-1] if not s.empty else None
