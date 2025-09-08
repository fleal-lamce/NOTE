import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


class LineGraph:
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.variable  = 'temperature'
        self.fig = go.Figure()
        self.ymin = 0
        self.ymax = 0
        self.value = 0

    def empty(self):
        self.fig = go.Figure()
        self.fig.update_layout(
            margin=dict(l=12, r=12, t=6, b=6),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#0c1628",
            xaxis=dict(showgrid=False, color="#94a3b8"),
            yaxis=dict(showgrid=False, color="#94a3b8", title=''),
            font=dict(color="#e5e7eb"),
        )

    def update(self):
        self.title = f'Gráfico Temporal - {self.variable}'
        color = '#60a5fa'
        fill  = 'rgba(96,165,250,0.15)'

        if self.dashboard.analysis.df.empty:
            return self.empty()
        
        if self.variable not in self.dashboard.analysis.df.columns:
            return self.empty()

        fig = go.Figure()
        x = self.dashboard.analysis.df.time
        y = self.dashboard.analysis.df[self.variable].values
        y_min, y_max = (float(y.min()), float(y.max())) if len(y) else (None, None)

        if y_min is not None:
            fig.add_trace(go.Scatter(
                x=list(x) + list(x[::-1]),
                y=list(y) + [y_min]*len(y),
                fill="toself",
                fillcolor=fill,
                line=dict(color="rgba(0,0,0,0)"),
                hoverinfo="skip",
                showlegend=False,
            ))

        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines",
            line=dict(width=3, color=color),
            name='value'
        ))

        fig.update_layout(
            margin=dict(l=12, r=12, t=12, b=6),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#0c1628",
            xaxis=dict(showgrid=False, color="#94a3b8"),
            yaxis=dict(showgrid=False, color="#94a3b8", title=''),
            font=dict(color="#e5e7eb"),
            hovermode="x unified",
            legend=dict(
                yanchor="bottom",  # ancora embaixo
                y=0.02,            # mais para baixo (0=base do plot, 1=topo)
                xanchor="right",
                x=0.98,            # perto da direita
                bgcolor="rgba(0,0,0,0)",
                font=dict(size=11, color="#e5e7eb")
            )
        )

        self.fig  = fig
        self.ymin = y_min
        self.ymax = y_max
        self.value = self.dashboard.analysis.getLastVar(self.variable)
