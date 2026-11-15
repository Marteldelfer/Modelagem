"""Classe base: cada gráfico declara o agrupamento e como desenhar a figura."""
import plotly.graph_objects as go
from dash import Input, Output, dcc, html

from sidebar import STORE_ID
from consultas import consultar

ESCALA, UNIDADE = 1e9, "R$ bi"          # valores dos gráficos em bilhões
TEMPLATE = "plotly_white"
NOMES = {
    "orcamento_inicial": "Inicial",
    "orcamento_atualizado": "Atualizado",
    "orcamento_empenhado": "Empenhado",
    "orcamento_realizado": "Realizado",
}
CORES = {"Inicial": "#9aa5b1", "Atualizado": "#1f77b4", "Empenhado": "#ff9f1c", "Realizado": "#2a9d8f"}


def _pt(s: str) -> str:
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_brl(v: float) -> str:
    for lim, suf in ((1e12, "tri"), (1e9, "bi"), (1e6, "mi"), (1e3, "mil")):
        if abs(v) >= lim:
            return _pt(f"R$ {v / lim:,.2f} {suf}")
    return _pt(f"R$ {v:,.2f}")


def fmt_pct(v: float) -> str:
    return _pt(f"{v:.1f}%")


def figura_vazia(msg="Sem dados para os filtros selecionados") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False, font=dict(size=14, color="#888"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(template=TEMPLATE, height=300)
    return fig


class Grafico:
    id: str
    titulo: str
    agrupar_por: list = []
    largura: int = 1          # 1 = meia linha, 2 = linha inteira
    altura: int = 380

    def figura(self, df):     # df já em bilhões
        raise NotImplementedError

    def layout(self):
        return html.Div([
            html.H5(self.titulo, className="card-title"),
            dcc.Loading(dcc.Graph(id=self.id, config={"displayModeBar": False})),
        ], className="card card-wide" if self.largura == 2 else "card")

    def register_callbacks(self, app):
        @app.callback(Output(self.id, "figure"), Input(STORE_ID, "data"))
        def _atualizar(filtros):
            df = consultar(self.agrupar_por, filtros or {})
            if df.empty:
                return figura_vazia()
            for m in NOMES:
                df[m] = df[m] / ESCALA
            fig = self.figura(df)
            fig.update_layout(template=TEMPLATE, height=self.altura, legend_title_text="",
                              margin=dict(l=10, r=10, t=10, b=10))
            return fig
