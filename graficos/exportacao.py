"""Botões de exportação (CSV / Excel) do header: exportam as linhas da fato com os filtros aplicados."""
from datetime import date

from dash import Input, Output, State, ctx, dcc, html, no_update

from consultas import contar_linhas, detalhar
from sidebar import STORE_ID

LIMITE_XLSX = 1_048_575          # linhas de dados que cabem numa planilha do Excel
CSV_SEP, CSV_DECIMAL = ";", ","  # padrão brasileiro (abre direto no Excel); use ",", "." se preferir


class Exportacao:
    csv_id, xlsx_id = "exp-csv", "exp-xlsx"
    download_id, status_id = "exp-download", "exp-status"

    def layout(self):
        return html.Div([
            dcc.Loading(html.Span(id=self.status_id, className="export-status"), type="circle"),
            html.Button("Exportar CSV", id=self.csv_id, n_clicks=0, className="btn-export"),
            html.Button("Exportar Excel", id=self.xlsx_id, n_clicks=0, className="btn-export"),
            dcc.Download(id=self.download_id),
        ], className="export-buttons")

    def register_callbacks(self, app):
        @app.callback(
            Output(self.download_id, "data"),
            Output(self.status_id, "children"),
            Input(self.csv_id, "n_clicks"),
            Input(self.xlsx_id, "n_clicks"),
            State(STORE_ID, "data"),
            prevent_initial_call=True,
        )
        def _exportar(_csv, _xlsx, filtros):
            formato = "csv" if ctx.triggered_id == self.csv_id else "xlsx"
            filtros = filtros or {}

            if formato == "xlsx" and contar_linhas(filtros) > LIMITE_XLSX:
                return no_update, "Linhas demais para o Excel: use CSV ou refine os filtros."

            df = detalhar(filtros)
            nome = f"orcamento_despesa_{date.today():%Y%m%d}.{formato}"
            if formato == "csv":
                # BOM para o Excel reconhecer o UTF-8
                texto = "\ufeff" + df.to_csv(index=False, sep=CSV_SEP, decimal=CSV_DECIMAL)
                return dcc.send_string(texto, nome), ""
            return dcc.send_data_frame(df.to_excel, nome, sheet_name="Orçamento", index=False), ""
