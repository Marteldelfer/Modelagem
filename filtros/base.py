"""Filtro hierárquico genérico: uma dimensão = vários dropdowns encadeados.

Cada dropdown só mostra opções compatíveis com as seleções dos níveis acima.
Todo filtro (inclusive o de tempo) expõe a mesma interface:
    table, key_col, layout(), register_callbacks(app), inputs, parse(values), keys(selection)
"""
from dataclasses import dataclass
from typing import Optional

import pandas as pd
from dash import Input, Output, State, dcc, html

from data import load_dimension


@dataclass(frozen=True)
class Level:
    id: str                      # sufixo do id do componente
    label: str                   # rótulo exibido
    code: str                    # coluna usada como valor do filtro
    name: Optional[str] = None   # coluna opcional exibida junto ao código


class HierarchicalFilter:
    def __init__(self, prefix: str, title: str, table: str, key_col: str, levels: list[Level]):
        self.prefix, self.title = prefix, title
        self.table, self.key_col = table, key_col
        self.levels = levels
        self.ids = [f"{prefix}-{lv.id}" for lv in levels]

    # ---------- dados ----------
    @property
    def df(self) -> pd.DataFrame:
        return load_dimension(self.table)

    def _select(self, df: pd.DataFrame, values: dict) -> pd.DataFrame:
        for lv, comp_id in zip(self.levels, self.ids):
            vals = values.get(comp_id)
            if vals:
                df = df[df[lv.code].isin(vals)]
        return df

    def _options(self, i: int, df: pd.DataFrame) -> list[dict]:
        lv = self.levels[i]
        cols = [lv.code] + ([lv.name] if lv.name else [])
        uniq = df[cols].dropna(subset=[lv.code]).drop_duplicates(subset=lv.code).sort_values(lv.code)
        return [
            {"label": f"{r[lv.code]} - {r[lv.name]}" if lv.name else str(r[lv.code]), "value": r[lv.code]}
            for _, r in uniq.iterrows()
        ]

    # ---------- interface do filtro ----------
    @property
    def inputs(self):
        return [Input(i, "value") for i in self.ids]

    def parse(self, values) -> dict:
        """Valores dos dropdowns -> {coluna: [valores]} (só o que foi selecionado)."""
        return {lv.code: v for lv, v in zip(self.levels, values) if v}

    def keys(self, selection: dict) -> Optional[list]:
        """Chaves substitutas (key_*) da dimensão para a seleção; None = sem filtro."""
        if not selection:
            return None
        df = self.df
        for col, vals in selection.items():
            df = df[df[col].isin(vals)]
        return df[self.key_col].tolist()

    # ---------- layout ----------
    def layout(self):
        df = self.df
        dropdowns = []
        for i, (lv, comp_id) in enumerate(zip(self.levels, self.ids)):
            dropdowns.append(html.Div([
                html.Label(lv.label, className="filter-label"),
                dcc.Dropdown(
                    id=comp_id,
                    options=self._options(i, df) if i == 0 else [],
                    multi=True,
                    placeholder="Todos",
                ),
            ], className="filter-item"))
        return html.Div([
            html.Div([
                html.H6(self.title, className="filter-title"),
                html.Button("Limpar", id=f"{self.prefix}-reset", n_clicks=0, className="btn-reset"),
            ], className="filter-header"),
            *dropdowns,
        ], className="filter-block")

    # ---------- callbacks ----------
    def register_callbacks(self, app):
        # nível i recalcula opções (e descarta valores inválidos) conforme os níveis acima
        for i in range(1, len(self.levels)):
            self._register_level(app, i)

        @app.callback(
            [Output(c, "value", allow_duplicate=True) for c in self.ids],
            Input(f"{self.prefix}-reset", "n_clicks"),
            prevent_initial_call=True,
        )
        def _reset(_):
            return [None] * len(self.ids)

    def _register_level(self, app, i: int):
        parents = self.ids[:i]

        @app.callback(
            Output(self.ids[i], "options"),
            Output(self.ids[i], "value"),
            [Input(p, "value") for p in parents],
            State(self.ids[i], "value"),
        )
        def _update(*args):
            sel = dict(zip(parents, args[:i]))
            options = self._options(i, self._select(self.df, sel))
            valid = {o["value"] for o in options}
            current = [v for v in (args[i] or []) if v in valid]
            return options, current or None
