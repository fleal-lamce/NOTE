import pandas as pd
from globals.variables import *
import plotly.express as px
import plotly.graph_objects as go


class LineGraph:
    def __init__(self):
        self.df    = pd.DataFrame()
        self.title = 'Gráfico Temporal'

    def update(self, dataframe):
        self.df = dataframe.copy().tail(50)

    def render(self, variable='temperature'):
        self.title = f'Gráfico Temporal - {variable}'
        data  = UNITS[variable]
        unit  = data.get('unit')
        color = data.get('color')
        fill  = data.get('fill')
        fig = go.Figure()

        if self.df.empty:
            fig.update_layout(
                margin=dict(l=12, r=12, t=6, b=6),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#0c1628",
                height=260,
                xaxis=dict(showgrid=False, color="#94a3b8"),
                yaxis=dict(showgrid=False, color="#94a3b8", title=unit),
                font=dict(color="#e5e7eb"),
            )

            return fig, None, None

        x = self.df.time
        y = self.df[variable]
        y_min, y_max = (float(y.min()), float(y.max())) if len(y) else (None, None)

        if y_min is not None:
            fig.add_trace(go.Scatter(
                x=list(x) + list(x[::-1]),
                y=list(y) + [y_min]*len(y),
                fill="toself",
                fillcolor=fill,
                line=dict(color="rgba(0,0,0,0)"),
                hoverinfo="skip",
                showlegend=False
            ))

        # Line on top
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines",
            line=dict(width=3, color=color),
            name=data.get('label')
        ))

        fig.update_layout(
            margin=dict(l=12, r=12, t=6, b=6),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#0c1628",
            height=260,
            xaxis=dict(showgrid=False, color="#94a3b8"),
            yaxis=dict(showgrid=False, color="#94a3b8", title=unit),
            font=dict(color="#e5e7eb"),
            hovermode="x unified"
        )

        return fig, y_min, y_max