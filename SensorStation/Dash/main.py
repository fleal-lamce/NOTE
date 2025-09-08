import pandas as pd
from dash import Dash, html, Input, Output, State
from assets.index import Interface
from objects.analysis.index import Analysis
from objects.events.index import Events
from objects.table.index import Table
from objects.graph.index import LineGraph
from objects.map.index import GeoMap


class Dashboard:
    def __init__(self):
        self.app = Dash(__name__, assets_folder='assets', title='Sensor Station Dashboard - COPPE/UFRJ')
        self.analysis  = Analysis(self)
        self.interface = Interface(self)
        self.table  = Table(self)
        self.graph  = LineGraph(self)
        self.map    = GeoMap(self)
        self.events = Events()

        self.analysis.download()
        self.analysis.update()
        self.table.update()
        self.graph.update()
        self.callbaks()

    def start(self):
        self.app.layout = html.Div(className="Page", children=self.interface.render())
        self.app.run(host='0.0.0.0', port=8050, debug=False)

    def callbaks(self):
        outputs = [
            Output('clocktime', 'children'),
            Output('temperature-var', 'children'),
            Output('humidity-var', 'children'),
            Output('pressure-var', 'children'),
            Output('wind-var', 'children'),
            Output('graph-date', 'children'),
            Output('graph-last-val', 'children'),
            Output('tbody', 'children'),
            Output('chart', 'figure'),
        ]

        inputs = [
            Input('update-button', 'n_clicks'),
            Input('var-select', 'value'),
            Input('area-select', 'value'),
            Input('device-select', 'value'),
        ]

        @self.app.callback(outputs, inputs)
        def render(btn1, varkey, area, device):
            if self.events.clicked('update-button'):
                self.analysis.download()

            self.analysis.device = device
            self.analysis.area   = area
            self.graph.variable  = varkey
            print(varkey, area, device)

            self.analysis.update()
            self.table.update()
            self.graph.update()

            return [
                f'LastSync: {self.analysis.curr_time}',
                f'{self.analysis.temperature}ºC',
                f'{self.analysis.humidity}%',
                f'{self.analysis.pressure}atm',
                f'{self.analysis.wind}m/s',
                f'Atualizado em {self.analysis.timestamp}',
                f'Último Valor: {self.graph.value} | Faixa: {self.graph.ymin} - {self.graph.ymax}',
                self.table.rows,
                self.graph.fig,
            ]
        
        @self.app.callback(Output('rjmap', "figure"), Input('rjmap', "relayoutData"), State('rjmap', "figure"), State('rjmap-points', "data"))
        def updateMap(relayout, current_fig, pontos):
            self.map.update(relayout, current_fig, pontos)
            return self.map.fig

        @self.app.callback(Output("down-xlsx", "data"), Input("export-button", "n_clicks"), prevent_initial_call=True)
        def downloadTable(n_clicks):
            return self.table.download()


if __name__ == '__main__':
    dashboard = Dashboard()
    dashboard.start()