"""Filtro de dim_tempo: seletor de intervalo de exercícios (independente dos demais)."""
from dash import Input, Output, dcc, html

from data import load_dimension


class TempoFilter:
    table = "dim_tempo"
    key_col = "key_tempo"
    col_ano = "exercicio"
    slider_id = "tempo-exercicio"
    reset_id = "tempo-reset"

    @property
    def df(self):
        return load_dimension(self.table)

    @property
    def inputs(self):
        return [Input(self.slider_id, "value")]

    def _range(self):
        anos = self.df[self.col_ano].dropna().astype(int)
        return int(anos.min()), int(anos.max())

    def parse(self, values) -> dict:
        (intervalo,) = values
        if not intervalo:
            return {}
        ini, fim = intervalo
        return {self.col_ano: list(range(ini, fim + 1))}

    def keys(self, selection: dict):
        if not selection:
            return None
        df = self.df
        return df[df[self.col_ano].isin(selection[self.col_ano])][self.key_col].tolist()

    def layout(self):
        lo, hi = self._range()
        return html.Div([
            html.Div([
                html.H6("Tempo", className="filter-title"),
                html.Button("Limpar", id=self.reset_id, n_clicks=0, className="btn-reset"),
            ], className="filter-header"),
            html.Div([
                html.Label("Exercício", className="filter-label"),
                dcc.RangeSlider(
                    id=self.slider_id, min=lo, max=hi, step=1, value=[lo, hi],
                    marks={a: str(a) for a in range(lo, hi + 1)},
                    allowCross=False,
                ),
            ], className="filter-item"),
        ], className="filter-block")

    def register_callbacks(self, app):
        lo, hi = self._range()

        @app.callback(
            Output(self.slider_id, "value", allow_duplicate=True),
            Input(self.reset_id, "n_clicks"),
            prevent_initial_call=True,
        )
        def _reset(_):
            return [lo, hi]
