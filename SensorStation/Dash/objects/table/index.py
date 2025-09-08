import pandas as pd
from dash import html, dcc

class Table:
    def __init__(self, dashboard):
        self.dasboard = dashboard
        self.rows = list()

    def getVar(self, row, varkey):
        return row[varkey] if pd.notna(row[varkey]) else '- '

    def getTime(self, row):
        return pd.to_datetime(row.time).strftime('%d/%m/%Y %H:%M') if pd.notna(row.time) else '- '

    def update(self):
        self.rows = list()
        df = self.dasboard.analysis.df[::-1]

        for i, row in df.iterrows():
            self.rows.append(html.Tr(children=[
                html.Td(self.getTime(row)),
                html.Td(self.getVar(row, 'temperature')),
                html.Td(self.getVar(row, 'humidity')),
                html.Td(self.getVar(row, 'esp_id')),
            ]))
        
    def download(self):
        print('oooooooooooiio')
        return dcc.send_data_frame(self.dasboard.analysis.df.to_excel, 'relatorio.xlsx', index=False)
    