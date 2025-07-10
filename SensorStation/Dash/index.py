import time, ast, sqlite3
import pandas as pd
import dash
from dash import html, dcc, Output, Input
import plotly.express as px


class Dashboard:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.reset()
        self.setup()
        self.callbacks()

    def reset(self):
        conn = sqlite3.connect('../server/db.sqlite3')
        self.df = pd.read_sql_query('SELECT * FROM Logs_log', conn)
        self.df['data'] = self.df.data.apply(ast.literal_eval)
        self.target = self.df.copy()

        self.variables = {
            'selected' : 'temperature',
            'variables': [var for var in self.df.data[0].keys()],
            'devices': self.df.esp_id.unique().tolist(),
            'start_date': None,
            'end_date': None
        }

    def run(self):
        self.app.run(host='0.0.0.0', port=8050, debug=False)

    def callbacks(self):
        @self.app.callback(Output('varplot1', 'figure'), Input('dropdown1', 'value'))
        def selectUpdate(selected):
            self.variables['selected'] = selected
            return self.lineGraph()
        
        @self.app.callback(Output('varplot2', 'figure'), Input('dropdown2', 'value'))
        def deviceUpdate(selected):
            self.variables['devices'] = [selected]
            self.target = self.df.loc[self.df.esp_id.isin([selected])]
            return self.pieGraph()

    def lineGraph(self):
        selected = self.variables.get('selected')
        labels   = {selected: selected.title(), 'date': 'Horário'}
        self.target[selected] = [row[selected] for row in self.target.data] 
        print(self.target)

        fig = px.line(self.target, x='date', y=selected, color='esp_id', labels=labels, title='Gráfico Temporal')
        fig.update_layout(legend={'x': 0.99, 'y': 0.99, 'xanchor': 'right', 'yanchor': 'top'})
        return fig
    
    def pieGraph(self):
        fig = px.pie(self.target, names=['Temperatura', 'Umidade', 'Outro'], values=[1, 3, 10], title='Distribuição por ESP')
        fig.update_layout(legend={'x': 0.97, 'y': 0.97, 'xanchor': 'right', 'yanchor': 'bottom'})
        return fig

    def setup(self):
        page = html.Div([
            html.H1('Sensor Station Dashboard', className='titlepage'),
            html.Label('Selecione a Variável',  className='subtitle'),

            html.Div([
                dcc.Dropdown(
                    id='dropdown1',
                    options=[{'label': var.title(), 'value': var} for var in self.df.data[0].keys()],
                    value='temperature',
                    className='dropdown'
                ),

                dcc.Dropdown(
                    id='dropdown2',
                    options=[{'label': id.upper(), 'value': id} for id in self.variables.get('devices') + ['Todos']],
                    value='Todos',
                    className='dropdown'
                ),
            ], className='dropdowns'),

            html.Div([
                dcc.Graph(id='varplot1', className='varplot', figure=self.lineGraph()),
                dcc.Graph(id='varplot2', className='varplot', figure=self.pieGraph())
            ], className='graphs')
        ], className='main')
        
        self.app.layout = html.Div(page, className='outer')


if __name__ == '__main__':
    window = Dashboard()
    window.run()
