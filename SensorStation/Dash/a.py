# pip install dash plotly
from dash import Dash, dcc, html, Output, Input, State
import plotly.express as px
import pandas as pd
import re

# ---------------------------
# 1) Dados de exemplo (RJ)
# ---------------------------
data = [
    {
        "nome": "Cristo Redentor",
        "lat": -22.9519, "lon": -43.2105,
        "label_md": "**Cristo Redentor**\n\n- Cartão-postal do RJ\n- Vista 360°\n\n*Dica:* vá cedo."
    },
    {
        "nome": "Pão de Açúcar",
        "lat": -22.9486, "lon": -43.1566,
        "label_md": "**Pão de Açúcar**\nBondinho clássico com vistas do Guanabara."
    },
    {
        "nome": "Maracanã",
        "lat": -22.9121, "lon": -43.2302,
        "label_md": "**Maracanã**\n\n- Estádio histórico\n- Tours e jogos"
    },
    {
        "nome": "Aterro do Flamengo",
        "lat": -22.9362, "lon": -43.1702,
        "label_md": "**Aterro do Flamengo**\nParque à beira da baía; bom pra pedalar."
    },
]

df = pd.DataFrame(data)

# ---------------------------------------
# 2) Conversor simples de Markdown -> HTML
#    (suficiente p/ hover; ajuste se quiser)
# ---------------------------------------
def md_to_html(md: str) -> str:
    html = md.strip()
    # bold **texto**
    html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html)
    # italic *texto*
    html = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", html)
    # listas "- item"
    html = re.sub(r"(?m)^\s*-\s+(.*)$", r"• \1", html)
    # quebras duplas viram <br><br>
    html = html.replace("\n\n", "<br><br>")
    # sobra de \n vira <br>
    html = html.replace("\n", "<br>")
    return html

df["hover_html"] = df["label_md"].map(md_to_html)

# ------------------------------------------------
# 3) Figura inicial (sem labels; só hover interativo)
# ------------------------------------------------
center_rio = {"lat": -22.9068, "lon": -43.1729}  # Centro aproximado do RJ

fig = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    hover_name="nome",
    hover_data=None,
    custom_data=["hover_html", "nome"],  # 0=html, 1=nome
    zoom=10,
    center=center_rio,
)
fig.update_traces(
    marker=dict(size=10),
    # Hover com HTML (Plotly aceita um subset de HTML seguro)
    hovertemplate="<b>%{customdata[1]}</b><br>%{customdata[0]}<extra></extra>",
    text=None,  # labels desligados inicialmente
)

# Sem token: use estilo OSM
fig.update_layout(
    mapbox_style="open-street-map",
    margin=dict(l=0, r=0, t=0, b=0),
)

# ------------------------------------------------
# 4) App Dash com callback que mostra labels por zoom
# ------------------------------------------------
app = Dash(__name__)
app.layout = html.Div(
    style={"height": "100vh", "display": "flex", "flexDirection": "column"},
    children=[
        html.Div(
            [
                html.H3("Mapa nativo Plotly — Rio de Janeiro (labels por zoom)"),
                html.P("Passe o mouse para ver o popup (Markdown → HTML). "
                       "Labels aparecem quando o zoom ≥ 12."),
            ],
            style={"padding": "10px 12px"}
        ),
        dcc.Graph(
            id="mapa-rj",
            figure=fig,
            style={"flex": 1, "minHeight": 400},
            config={"displayModeBar": True},
        ),
        dcc.Store(id="store-pontos", data=df.to_dict("records")),
    ]
)

@app.callback(
    Output("mapa-rj", "figure"),
    Input("mapa-rj", "relayoutData"),
    State("mapa-rj", "figure"),
    State("store-pontos", "data"),
    prevent_initial_call=True,
)
def toggle_labels_by_zoom(relayout, current_fig, pontos):
    # Copia figura atual
    import plotly.graph_objects as go
    fig = go.Figure(current_fig)

    # Determina zoom atual; fallback para 10
    zoom = None
    if relayout:
        # chaves possíveis: 'mapbox.zoom' ou 'mapbox._derived.zoom'
        zoom = relayout.get("mapbox.zoom", relayout.get("mapbox._derived", {}).get("zoom"))
    if zoom is None:
        zoom = current_fig.get("layout", {}).get("mapbox", {}).get("zoom", 10)

    # Regra de visibilidade de labels
    show_labels = zoom >= 12

    # Define 'text' quando deve mostrar label (ex.: o 'nome')
    text_values = [p["nome"] for p in pontos] if show_labels else [None] * len(pontos)

    # Atualiza o primeiro (e único) trace de pontos
    fig.update_traces(text=text_values, textposition="top right")

    # (Opcional) ajustar tamanho dos marcadores conforme zoom
    # Ex.: crescer um pouco acima de 13
    marker_size = 10 if zoom < 13 else 12
    fig.update_traces(marker=dict(size=marker_size))

    return fig

if __name__ == "__main__":
    app.run(debug=True)
