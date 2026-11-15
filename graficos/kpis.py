from dash import Input, Output, html

from consultas import consultar
from graficos.base import NOMES, fmt_brl, fmt_pct
from sidebar import STORE_ID


class Kpis:
    id = "kpis"

    def layout(self):
        return html.Div(id=self.id, className="kpis")

    def register_callbacks(self, app):
        @app.callback(Output(self.id, "children"), Input(STORE_ID, "data"))
        def _atualizar(filtros):
            t = consultar([], filtros or {}).iloc[0]
            ini, atu, emp, rea = (t[m] for m in NOMES)
            cards = [(NOMES[m], fmt_brl(t[m])) for m in NOMES]
            cards += [
                ("% Empenhado", fmt_pct(100 * emp / atu) if atu else "–"),
                ("% Realizado", fmt_pct(100 * rea / atu) if atu else "–"),
            ]
            return [html.Div([html.Div(r, className="kpi-label"), html.Div(v, className="kpi-value")],
                             className="kpi") for r, v in cards]
