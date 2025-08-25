from dash import html, dcc


class Interface:
    def __init__(self, dashboard):
        self.dashboard = dashboard

    def logo(self):
        return html.Div(className="logos-container", children=[
            html.Img(
                src="/assets/images/grva.png",
                className='logoimage'
            ),
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
        return html.Div(className='show-variable', children=[
            html.Div(className='logo-var'),
            
            html.Div(className='info-var-container', children=[
                html.Div(label, className='info-var-label'),
                html.Div('Valor', id=id, className='info-var-value'),
                html.Div()
            ]),
            html.Div('variação de ±2%', id=f'altern-{id}', className='info-var-altern')
        ])
    
    def graph(self):
        return html.Div(className='graph-container', children=[
            html.Div(className='graph-title', children=[
                html.Div('Gráfico Temporal - Variável', id='graph-title', className='graph-title-left'),
                html.Div('Atualizado em dd/mm/yy - 13:12:11', id='graph-date', className='graph-title-right')
            ]),
            
            html.Div(className='line-graph', children=[
                dcc.Graph(id="chart", config={"displayModeBar": False}, style={'width': '100%', 'height': '100%'})
            ]),
            html.Div('Último Valor: 90% | Faixa: 40.0 - 89%', className='graph-bottom', id='graph-last-val')
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

    def render(self):
        return html.Header(className='App', children=[
            html.Div(className='first-row', children=[
                self.logo(),
                self.input('Variável:',  self.dashboard.analysis.variables, 'var-select'),
                self.input('Área Alvo:', self.dashboard.analysis.areas, 'area-select'),
                self.input('ID Device:', self.dashboard.analysis.devices, 'device-select'),
                html.Button("Atualizar", id="update-button", n_clicks=0, title="Recarregar do CSV", className='update-button'),
            ]),
            
            html.Div(className='second-row', children=[
                self.variable('Temperatura', 'temperature-var'),
                self.variable('Umidade', 'humidity-var'),
                self.variable('Pressão', 'pressure-var'),
                self.variable('Vento', 'wind-var'),
            ]),
            
            html.Div(className='third-row', children=[
                self.graph(),
                self.table(),
            ]),
        ])