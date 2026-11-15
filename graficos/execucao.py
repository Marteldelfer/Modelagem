import plotly.express as px

from graficos.base import CORES, Grafico


class ExecucaoAnual(Grafico):
    id = "g-execucao"
    titulo = "Execução (% do orçamento atualizado)"
    agrupar_por = [("dim_tempo", "exercicio")]

    def figura(self, df):
        df = df.sort_values("exercicio")
        d = df[["exercicio"]].copy()
        d["Empenhado"] = 100 * df["orcamento_empenhado"] / df["orcamento_atualizado"]
        d["Realizado"] = 100 * df["orcamento_realizado"] / df["orcamento_atualizado"]
        longo = d.melt(id_vars="exercicio", var_name="medida", value_name="pct")
        fig = px.line(longo, x="exercicio", y="pct", color="medida", markers=True,
                      color_discrete_map=CORES, labels={"pct": "% do atualizado", "exercicio": ""})
        fig.update_xaxes(type="category")
        fig.update_traces(hovertemplate="%{x} · %{fullData.name}: %{y:.1f}%<extra></extra>")
        return fig
