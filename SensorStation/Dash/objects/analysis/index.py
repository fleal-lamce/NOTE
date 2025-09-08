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
        self.ALL_AREAS   = pd.read_sql_query('SELECT * FROM Areas_area', sqlite3.connect('../Server/db.sqlite3'))
        self.ALL_DEVICES = pd.read_sql_query('SELECT * FROM Devices_device', sqlite3.connect('../Server/db.sqlite3'))

    def download(self):
        LIMIT = 15000
        QUERY = f'SELECT * FROM (SELECT * FROM Logs_log ORDER BY id DESC LIMIT {LIMIT}) AS subquery_alias ORDER BY id ASC;'
        conn  = sqlite3.connect('../Server/db.sqlite3')
        df    = pd.read_sql_query(QUERY, conn)

        self.database = pd.concat([
            pd.to_datetime(df.timestamp, errors='coerce', utc=True).dt.tz_convert('America/Sao_Paulo').dt.tz_localize(None),
            df.esp_id,
            pd.json_normalize(df.data.apply(ast.literal_eval))
        ], axis=1)

        self.database.rename(columns={'timestamp': 'time'}, inplace=True)
        self.devices = [{'label': 'todos', 'value': 'all'}] + [{'label': self.getID(id), 'value': id} for id in self.database.esp_id.unique()]
        self.areas   = [{'label': 'todos', 'value': 'all'}] + [{'label': self.getArea(area), 'value': area} for area in self.ALL_AREAS.value.unique()]

    def update(self):
        self.df = self.database.copy()

        if self.area != 'all':
            target  = self.ALL_DEVICES.loc[self.ALL_DEVICES.area == self.area]
            self.df = self.df.loc[self.df.esp_id.isin(target.esp_id.values)]

        if self.device != 'all':
            self.df = self.df.loc[self.df.esp_id == self.device]

        self.curr_time = datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')
        self.timestamp = self.getLastVar('time').strftime('%d/%m/%Y %H:%M:%S') if self.getLastVar('time') else 'N/A'
        self.temperature = self.getLastVar('temperature', number=True, errors='- ')
        self.humidity = self.getLastVar('humidity', number=True, errors='- ')
        self.pressure = self.getLastVar('pressure', number=True, errors='- ')
        self.wind = self.getLastVar('wind', number=True, errors='- ')

        if len(self.df) > 150:
            self.df = self.df.tail(150)

    def getLastVar(self, key, number=False, errors=None):
        s = self.df.get(key)

        if s is None:
            return errors
        
        s = s.dropna()
        if number:
            return float(s.iloc[-1]) if not s.empty else errors

        return s.iloc[-1] if not s.empty else errors

    def getID(self, id):
        target = self.ALL_DEVICES.loc[self.ALL_DEVICES.esp_id == id]

        if len(target) == 0:
            return None

        node   = self.ALL_DEVICES.iloc[0].node
        area   = self.ALL_DEVICES.iloc[0].area
        target = self.ALL_AREAS.loc[self.ALL_AREAS.value == area]
        
        
        if len(target) == 0:
            return None
        
        label = target.iloc[0].label
        return f'{id} - {label} - {node}'
    
    def getArea(self, area):
        target = self.ALL_AREAS.loc[self.ALL_AREAS.value == area]
        return target.iloc[0].label if len(target) > 0 else 'NULL'
