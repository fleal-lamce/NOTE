from dash import html, dcc, Output, Input
from globals.variables import UNITS

page = [
    html.Header(children=[
        html.Div(className="brand", children=[
            html.Img(
                src="/assets/images/grva.png",
                className="brand-logo",
            ),
            html.Div(children=[
                html.H1("Estação Sensorial - Lamce/GRVA"),
                html.Div(f"Dash time", className="sub", id='now-time')
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
                            html.Th("ID"),
                        ])
                    ]),
                    html.Tbody(id="tbody")
                ])
            ])
        ])
    ])
]