"""Lista de gráficos do painel. Para incluir/remover um gráfico, edite só GRAFICOS."""
from dash import html

from graficos.evolucao import EvolucaoAnual
from graficos.execucao import ExecucaoAnual
from graficos.funcao import FuncaoSubfuncao
from graficos.kpis import Kpis
from graficos.natureza import GrupoDespesa
from graficos.top_orgaos import TopOrgaos
from graficos.uf import PorUF

KPIS = Kpis()
GRAFICOS = [EvolucaoAnual(), ExecucaoAnual(), GrupoDespesa(), TopOrgaos(), FuncaoSubfuncao(), PorUF()]


def layout():
    return html.Div([KPIS.layout(), html.Div([g.layout() for g in GRAFICOS], className="grid")])


def register_callbacks(app):
    KPIS.register_callbacks(app)
    for g in GRAFICOS:
        g.register_callbacks(app)
