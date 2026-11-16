"""Painel principal: header (título + exportação), totais e gráficos.
Para incluir/remover um gráfico, edite só GRAFICOS."""
from dash import html

from graficos.evolucao import EvolucaoAnual
from graficos.execucao import ExecucaoAnual
from graficos.exportacao import Exportacao
from graficos.funcao import FuncaoSubfuncao
from graficos.kpis import Kpis
from graficos.natureza import GrupoDespesa
from graficos.top_orgaos import TopOrgaos
from graficos.uf import PorUF

EXPORTACAO = Exportacao()
KPIS = Kpis()
GRAFICOS = [EvolucaoAnual(), ExecucaoAnual(), GrupoDespesa(), TopOrgaos(), FuncaoSubfuncao(), PorUF()]


def layout():
    return html.Div([
        html.Div([html.H3("Orçamento da despesa"), EXPORTACAO.layout()], className="header"),
        KPIS.layout(),
        html.Div([g.layout() for g in GRAFICOS], className="grid"),
    ])


def register_callbacks(app):
    EXPORTACAO.register_callbacks(app)
    KPIS.register_callbacks(app)
    for g in GRAFICOS:
        g.register_callbacks(app)
