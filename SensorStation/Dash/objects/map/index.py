import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import re, os
import plotly.io as pio


mapINFO = [
    {
        "nome": "LAMCE/GRVA - COPPE/UFRJ",
        # Rua Sydiney Martins Gomes dos Santos, 179 (Parque Tecnológico)
        # fonte das coords da rua: guiamapa
        "lat": -22.862688,
        "lon": -43.225895,
        "label": "**LAMCE/GRVA – COPPE/UFRJ**\nParque Tecnológico da UFRJ."
    },
    {
        "nome": "Píer (ao lado do LAMCE)",
        # APROXIMADO — ajuste se tiver as coords exatas do píer
        "lat": -22.861900,
        "lon": -43.224800,
        "label": "**Píer ao lado do LAMCE**\nPonto de referência na orla."
    },
]



def getPDF(markdown):
    html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", markdown.strip())
    html = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", html)
    html = re.sub(r"(?m)^\s*-\s+(.*)$", r"• \1", html)
    return html.replace("\n\n", "<br><br>").replace("\n", "<br>")


class GeoMap:
    center = {"lat": -22.8610, "lon": -43.2230} 

    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.df = pd.DataFrame(mapINFO)
        self.df['hover_html'] = self.df.label.map(getPDF)

        self.fig = px.scatter_mapbox(
            self.df,
            lat="lat",
            lon="lon",
            hover_name="nome",
            hover_data=None,
            custom_data=["hover_html", "nome"],  # 0=html, 1=nome
            zoom=12,
            center=self.center,
        )

        self.fig.update_traces(
            marker=dict(
                size=12,
                color="#ff3b30",
                opacity=0.95,
                symbol="circle",
            ),
            hovertemplate="<b>%{customdata[1]}</b><br>%{customdata[0]}<extra></extra>",
            text=None,  # labels desligados inicialmente
        )

        self.fig.update_layout(
            mapbox_style="carto-darkmatter",  
            margin=dict(l=0, r=0, t=0, b=0),
        )
        
    def update(self, relayout, current_fig, pontos):
        self.fig = go.Figure(current_fig)
        zoom = None
        
        if relayout:
            zoom = relayout.get("mapbox.zoom", relayout.get("mapbox._derived", {}).get("zoom"))
        
        if zoom is None:
            zoom = current_fig.get("layout", {}).get("mapbox", {}).get("zoom", 10)

        show_labels = zoom >= 12  # ajuste seu limiar
        text_values = [p["nome"] for p in pontos] if show_labels else [None] * len(pontos)
        self.fig.update_traces(text=text_values, textposition="top right")

        marker_size = 10 if zoom < 13 else 12
        self.fig.update_traces(marker=dict(size=marker_size))

