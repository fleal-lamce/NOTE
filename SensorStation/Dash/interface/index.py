from dash import html, dcc, Output, Input
from globals.variables import *


class Interface:
    def legends(self, varkey, lastVal, y_min, y_max):
        return [
            html.Span("Último valor: "),
            html.B(f"{lastVal} {UNITS[varkey]['unit']}") if lastVal is not None else html.Span('—'),
            html.Span(" | "),
            html.Span("Faixa: "),
            html.B(f"{y_min} - {y_max} {UNITS[varkey]['unit']}") if y_min is not None and y_max is not None else html.Span('—'),
        ]


interface = Interface()