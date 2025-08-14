import pandas as pd
from dash import html, dcc, Output, Input
from globals.variables import *


class Table:
    SIZE = 12

    def __init__(self):
        self.df = pd.DataFrame()

    def update(self, df, varkey):
        self.df = df.tail(self.SIZE).iloc[::-1]
        self.last_val = self.df.iloc[-1][varkey]
        self.rows = []

        for i, row in self.df.iterrows():
            time = pd.to_datetime(row.time).strftime("%H:%M") if pd.notna(row.time) else "--:--"
            
            temp    = row['temperature'] if pd.notna(row['temperature']) else "—"
            hum     = row['humidity'] if pd.notna(row['humidity']) else "—"
            var_val = row[varkey] if pd.notna(row[varkey]) else "—"

            self.rows.append(html.Tr(children=[
                html.Td(time),
                html.Td(temp),
                html.Td(hum),
                html.Td(f"{var_val} {UNITS[varkey].get('unit', '')}"),
            ]))
                    
