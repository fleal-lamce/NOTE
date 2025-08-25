import time, ast, sqlite3
import pandas as pd
import dash
from dash import html, dcc, Output, Input
import plotly.express as px
from globals.variables import *
from globals.functions import *
from interface.index import interface
from assets.index import drawPage
from graphs.line import LineGraph
from graphs.table import Table
from graphs.status import Status
from dash import callback_context


class Dashboard:
    df = pd.DataFrame()
    time = getTime()

    def __init__(self):
        self.app = dash.Dash(__name__, assets_folder='assets', title='Sensor Station Dashboard - COPPE/UFRJ')
        self.download()
        self.setup()
        
        self.line = LineGraph()
        self.line.update(self.df)

        self.table  = Table()
        self.table.update(self.df, 'temperature')

        self.status = Status()
        self.status.update(self.df)

    def start(self):
        self.draw()
        self.app.run(host='0.0.0.0', port=8050, debug=False)

    def download(self):
        self.time = getTime()

        conn = sqlite3.connect('../server/db.sqlite3')
        self.df = pd.read_sql_query('SELECT * FROM Logs_log', conn)
        
        self.df['data'] = self.df.data.apply(ast.literal_eval)
        self.df['time'] = pd.to_datetime(self.df.timestamp, errors='coerce')
        
        self.df = pd.concat([
            self.df.time,
            self.df.esp_id,
            self.df.area,
            pd.json_normalize(self.df.data)
        ], axis=1)

        self.devices = [{'label': id, 'value': id} for id in self.df.esp_id.unique()]     + [{'label': 'todos', 'value': 'all'}]
        self.areas   = [{'label': area, 'value': area} for area in self.df.area.unique()] + [{'label': 'todos', 'value': 'all'}]

    def clicked(self, key):
        return callback_context.triggered and callback_context.triggered[0]["prop_id"].startswith(key)

    def setup(self):
        outputs = [
            Output("chart", "figure"),
            Output("chart-title", "children"),
            Output("last-update", "children"),
            Output("chart-legend", "children"),
            Output("kpi-temp", "children"),
            Output("kpi-temp-badge", "children"),
            Output("kpi-hum", "children"),
            Output("kpi-hum-badge", "children"),
            Output("kpi-press", "children"),
            Output("kpi-press-badge", "children"),
            Output("kpi-wind", "children"),
            Output("kpi-wind-badge", "children"),
            Output("tbody", "children"),
            Output("rows-count", "children"),
            Output("now-time", "children"),
        ]
        inputs = [
            Input("refresh-btn", "n_clicks"),
            Input("var-select", "value"),
            Input("area-select", "value"),
            Input("device-select", "value"),
        ]

        @self.app.callback(outputs, inputs)
        def render(n_clicks, varkey, area, device):
            if self.clicked("refresh-btn"):
                print('clicou')
                self.download()

            varkey = varkey or "temperature"
            
            print(device)
            
            if device and device != 'all':
                target = [device]
            else:
                target = list(self.df.esp_id.dropna().unique())
            
            df = self.df.loc[self.df.esp_id.isin(target)]

            self.line.update(df)
            fig, y_min, y_max = self.line.render(varkey)

            self.table.update(df, varkey)
            self.status.update(df)
            
            return [
                fig,
                self.line.title,
                self.status.info['last_update'],
                interface.legends(varkey, self.table.last_val, y_min, y_max),
                self.status.info['kpi_temp'],
                self.status.info['kpi_temp_badge'],
                self.status.info['kpi_hum'],
                self.status.info['kpi_hum_badge'],
                self.status.info['kpi_press'],
                self.status.info['kpi_press_badge'],
                self.status.info['kpi_wind'],
                self.status.info['kpi_wind_badge'],
                self.table.rows,                 # tbody
                self.table.SIZE,                 # rows-count
                f"Dash {self.time}",             # now-time
            ]

    def draw(self):
        self.app.layout = html.Div(className="container", children=drawPage(self.devices, self.areas))

    
if __name__ == '__main__':
    dashboard = Dashboard()
    dashboard.start()
