import time, ast, sqlite3
import pandas as pd
import dash
from dash import html, dcc, Output, Input
import plotly.express as px
from globals.variables import *
from globals.functions import *
from graphs.line import LineGraph
from graphs.table import Table
from graphs.status import Status
from dash import callback_context


class Dashboard:
    df = pd.DataFrame()
    time = getTime()

    def __init__(self):
        self.app  = dash.Dash(__name__, assets_folder='assets', title='Sensor Station Dashboard - COPPE/UFRJ')
        self.download()
        self.setup()
        
        self.line = LineGraph()
        self.line.update(self.df)

        self.table = Table()
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
            pd.json_normalize(self.df.data)
        ], axis=1)

        print(self.df)
        print(self.df.info())

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
            Output("th-var", "children"),
            Output("now-time", "children"),
        ]
        inputs = [
            Input("refresh-btn", "n_clicks"),
            Input("var-select", "value"),
        ]

        @self.app.callback(outputs, inputs)
        def render(n_clicks, varkey):
            if callback_context.triggered and callback_context.triggered[0]["prop_id"].startswith("refresh-btn"):
                print('clicou')
                self.download()

            varkey = varkey or "temperature"

            self.line.update(self.df)
            fig, y_min, y_max = self.line.render(varkey)

            self.table.update(self.df, varkey)
            self.status.update(self.df)
            
            legendChildren = [
                html.Span("Último valor: "),
                html.B(f"{self.table.last_val} {UNITS[varkey]['unit']}") if self.table.last_val is not None else html.Span('—'),
                html.Span(" | "),
                html.Span("Faixa: "),
                html.B(f"{y_min} - {y_max} {UNITS[varkey]['unit']}") if y_min is not None and y_max is not None else html.Span('—'),
            ]

            return [
                fig,
                self.line.title,
                self.status.info['last_update'],
                legendChildren,
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
                UNITS[varkey].get('label'),      # th-var
                f"Dash {self.time}",             # now-time
            ]

    def draw(self):
        self.app.layout = html.Div(className="container", children=[
            html.Header(children=[
                html.Div(className="brand", children=[
                    html.Div(className="brand-logo"),
                    html.Div(children=[
                        html.H1("Dashboard IoT"),
                        html.Div(f"Dash {self.time}", className="sub", id='now-time')
                    ])
                ]),
                html.Div(className="toolbar", children=[
                    html.Span("Dados de demonstração", className="pill demo"),
                    html.Label("Variável:", className="sub", htmlFor="var-select"),
                    dcc.Dropdown(
                        id="var-select",
                        options=[{"label": UNITS[k]["label"], "value": k} for k in UNITS.keys()],
                        value="humidity",
                        clearable=False,
                        style={"minWidth":"240px", 'color': 'black'}
                    ),
                    html.Button("Atualizar", id="refresh-btn", n_clicks=0, title="Recarregar do CSV", className='UpdateButton'),
                ], style={"display":"flex","gap":"12px","alignItems":"center","flexWrap":"wrap"})
            ]),

            html.Section(id="grid", className="grid", children=[
                # KPI cards
                html.Article(className="card kpi-card", children=[
                    html.Div(className="kpi", children=[
                        html.Div(className="left", children=[
                            html.Div(className="icon"),
                            html.Div(children=[
                                html.H3("Temperatura"),
                                html.Div("--°C", id="kpi-temp", className="val")
                            ])
                        ]),
                        html.Div("Sensação: --°C", id="kpi-temp-badge", className="badge")
                    ])
                ]),
                html.Article(className="card kpi-card", children=[
                    html.Div(className="kpi", children=[
                        html.Div(className="left", children=[
                            html.Div(className="icon"),
                            html.Div(children=[
                                html.H3("Umidade"),
                                html.Div("--%", id="kpi-hum", className="val")
                            ])
                        ]),
                        html.Div("Ponto de orvalho: --°C", id="kpi-hum-badge", className="badge")
                    ])
                ]),
                html.Article(className="card kpi-card", children=[
                    html.Div(className="kpi", children=[
                        html.Div(className="left", children=[
                            html.Div(className="icon"),
                            html.Div(children=[
                                html.H3("Pressão"),
                                html.Div("-- hPa", id="kpi-press", className="val")
                            ])
                        ]),
                        html.Div("Tendência: --", id="kpi-press-badge", className="badge")
                    ])
                ]),
                html.Article(className="card kpi-card", children=[
                    html.Div(className="kpi", children=[
                        html.Div(className="left", children=[
                            html.Div(className="icon"),
                            html.Div(children=[
                                html.H3("Vento"),
                                html.Div("-- m/s", id="kpi-wind", className="val")
                            ])
                        ]),
                        html.Div("Rajada: -- m/s", id="kpi-wind-badge", className="badge")
                    ])
                ]),

                # Chart card
                html.Article(className="card chart-card", children=[
                    html.Div(className="chart-head", children=[
                        html.H2("Histórico — Umidade (%)", id="chart-title", className="chart-title"),
                        html.Div("Atualizado: --:--", id="last-update", className="chart-sub")
                    ]),
                    html.Div(className="chart-box", children=[
                        dcc.Graph(id="chart", config={"displayModeBar": False})
                    ]),
                    html.Div(id="chart-legend", className="legend")
                ]),

                # Table card
                html.Article(className="card table-card", children=[
                    html.Div(className='TableContainer', children=[
                        html.H2("Últimas leituras", className="chart-title", style={"margin":"0"}),
                        html.Span("—", id="rows-count", className="pill")
                    ]),
                    html.Div(className="table-wrapper", children=[
                        html.Table(children=[
                            html.Thead(children=[
                                html.Tr(children=[
                                    html.Th("Hora"),
                                    html.Th("Temp (°C)"),
                                    html.Th("Umid (%)"),
                                    html.Th("Variável", id="th-var"),
                                ])
                            ]),
                            html.Tbody(id="tbody")
                        ])
                    ])
                ])
            ])
        ])

    
if __name__ == '__main__':
    dashboard = Dashboard()
    dashboard.start()
