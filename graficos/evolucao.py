import plotly.express as px

from graficos.base import CORES, NOMES, UNIDADE, Grafico


class EvolucaoAnual(Grafico):
    id = "g-evolucao"
    titulo = "Evolução anual do orçamento"
    agrupar_por = [("dim_tempo", "exercicio")]
    largura = 2

    def figura(self, df):
        longo = df.sort_values("exercicio").melt(
            id_vars="exercicio", value_vars=list(NOMES), var_name="medida", value_name="valor")
        longo["medida"] = longo["medida"].map(NOMES)
        fig = px.bar(longo, x="exercicio", y="valor", color="medida", barmode="group",
                     color_discrete_map=CORES, labels={"valor": UNIDADE, "exercicio": ""})
        fig.update_xaxes(type="category")
        fig.update_traces(hovertemplate="%{x} · %{fullData.name}: R$ %{y:,.2f} bi<extra></extra>")
        return fig
