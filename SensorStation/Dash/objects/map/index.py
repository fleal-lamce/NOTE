import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import re, os, sqlite3
import plotly.io as pio


def getPDF(markdown):
    html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", markdown.strip())
    html = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", html)
    html = re.sub(r"(?m)^\s*-\s+(.*)$", r"• \1", html)
    return html.replace("\n\n", "<br><br>").replace("\n", "<br>")


class GeoMap:
    center = {"lat": -22.8610, "lon": -43.2230} 

    def __init__(self, dashboard):
        self.locations = pd.read_sql_query('SELECT * FROM Locations_location', sqlite3.connect('../Server/db.sqlite3')).rename(columns={"lng": "lon"})
        self.locations = [row.to_dict() for i, row in self.locations.iterrows()]
        print(self.locations)

        self.dashboard = dashboard
        self.df = pd.DataFrame(self.locations)
        self.df['hover_html'] = self.df.label.map(getPDF)

        self.fig = px.scatter_mapbox(
            self.df,
            lat="lat",
            lon="lon",
            hover_name="label",
            hover_data=None,
            custom_data=["hover_html", "label"],  # 0=html, 1=nome
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
        text_values = [p["label"] for p in pontos] if show_labels else [None] * len(pontos)
        self.fig.update_traces(text=text_values, textposition="top right")

        marker_size = 10 if zoom < 13 else 12
        self.fig.update_traces(marker=dict(size=marker_size))

