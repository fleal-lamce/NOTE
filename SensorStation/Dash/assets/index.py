from dash import html, dcc


class Interface:
    def __init__(self, dashboard):
        self.dashboard = dashboard

    def logo(self):
        return html.Div(className="logos-container", children=[
            html.Img(src="/assets/images/grva.png", className='logoimage'),
            html.Div(children=[], style={'padding': '10px'}),
            html.Div(children=[
                html.Div("Estação Sensorial - Lamce/GRVA", className='titletext'),
                html.Div(f"Dash time", id='clocktime', className='subtitletext'),
            ], className='title-container')
        ])
    
    def input(self, label, options, id):
        return html.Div(className="dropdown-container", children=[
            html.Label(label, className="dropdown-label"),
            dcc.Dropdown(
                id=id,
                options=options,
                value=options[0]['value'],
                clearable=False,
                className='dropdown'
            ),
        ])
    
    def variable(self, label, id):
        img_name = id.split('-')[0].strip().lower()

        return html.Div(className='show-variable', children=[
            html.Img(src=f"/assets/images/{img_name}.png", className='logo-var'),

            html.Div(className='info-var-container', children=[
                html.Div(label, className='info-var-label'),
                html.Div('Valor', id=id, className='info-var-value'),
                html.Div()
            ])
        ])
    
    def graph(self):
        return html.Div(className='graph-container', children=[
            html.Div(className='graph-title', children=[
                html.Div('Último Valor: 90% | Faixa: 40.0 - 89%', className='graph-bottom', id='graph-last-val'),
                html.Div('Atualizado em dd/mm/yy - 13:12:11', id='graph-date', className='graph-title-right')
            ]), 
            
            html.Div(className='line-graph', children=[
                dcc.Graph(
                    id="chart", 
                    config={"displayModeBar": True, "displaylogo": False}, 
                    style={'width': '100%', 'height': '100%'}
                )
            ]),
            
            html.Div(className='graph-title', children=[
                html.Div(style={'width': '60%', 'color': 'black', 'height': '1.5rem'}, children=[
                    self.input('Variável:', self.dashboard.analysis.variables, 'var-select'),
                ])
            ])
        ])
    
    def table(self):
        return html.Div(className='table-container', children=[
            html.Div('Últimas Leituras', className='table-header'),
            
            html.Div(className='table-view', children=[
                html.Table(children=[
                    html.Thead(children=[
                        html.Tr(children=[
                            html.Th("Hora"),
                            html.Th("Temp (°C)"),
                            html.Th("Umid (%)"),
                            html.Th("ID"),
                        ])
                    ], style={'color': 'white'}),
                    html.Tbody(id="tbody", style={'color': 'white'})
                ])
            ]),

            html.Div(className='table-header')
        ])
    
    def map(self):
        return html.Div(className='table-container', children=[
            dcc.Graph(
                id='rjmap',
                figure=self.dashboard.map.fig,
                config={"displayModeBar": True},
                style={"height": "70vh", "minHeight": 400}
            ),
            dcc.Store(
                id=f"rjmap-points", 
                data=self.dashboard.map.df.to_dict("records")
            ),
        ], style={'width': '29%'})

    def render(self):
        return html.Header(className='App', children=[
            html.Div(className='first-row', children=[
                self.logo(),
                self.input('Área Alvo:', self.dashboard.analysis.areas, 'area-select'),
                self.input('ID Device:', self.dashboard.analysis.devices, 'device-select'),
                html.Button("Atualizar", id="update-button", n_clicks=0, title="Recarregar do CSV", className='update-button'),
            ]),
            
            html.Div(className='second-row', children=[
                self.variable('Temperatura', 'temperature-var'),
                self.variable('Umidade', 'humidity-var'),
                self.variable('Pressão', 'pressure-var'),
                self.variable('Vento', 'wind-var'),
                
                html.Button("Exportar Tabela", id="export-button", n_clicks=0, title="Download Excel", className='update-button'),
                dcc.Download(id="down-xlsx")
            ]),
            
            html.Div(className='third-row', children=[
                self.graph(),
                self.map(),
                self.table(),
            ]),
        ])