"""Painel lateral: junta os filtros. Para adicionar/remover uma dimensão, edite só a lista FILTROS."""
from dash import Input, Output, dcc, html

from filtros.localidade import localidade
from filtros.natureza_despesa import natureza_despesa
from filtros.orgao import orgao
from filtros.programa_acao import programa_acao
from filtros.tempo import TempoFilter

FILTROS = [TempoFilter(), localidade, programa_acao, natureza_despesa, orgao]
STORE_ID = "store-filtros"


def layout():
    return html.Div([
        html.H4("Filtros", className="sidebar-title"),
        *[f.layout() for f in FILTROS],
        dcc.Store(id=STORE_ID),
    ], className="sidebar")


def register_callbacks(app):
    for f in FILTROS:
        f.register_callbacks(app)

    todos_inputs = [i for f in FILTROS for i in f.inputs]

    @app.callback(Output(STORE_ID, "data"), todos_inputs)
    def _coletar(*values):
        """Consolida tudo em {dimensão: {coluna: [valores]}}."""
        saida, pos = {}, 0
        for f in FILTROS:
            n = len(f.inputs)
            saida[f.table] = f.parse(values[pos:pos + n])
            pos += n
        return saida


def chaves_selecionadas(filtros: dict) -> dict:
    """{dimensão: [key_*] ou None}. Use no WHERE da tabela fato: key_x IN (...)."""
    return {f.key_col: f.keys(filtros.get(f.table, {})) for f in FILTROS}
