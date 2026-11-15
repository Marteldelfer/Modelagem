import plotly.graph_objects as go

from graficos.base import CORES, UNIDADE, Grafico

TOP_N = 10


class TopOrgaos(Grafico):
    id = "g-top-orgaos"
    titulo = f"Top {TOP_N} órgãos superiores"
    agrupar_por = [("dim_orgao", "nome_orgao_superior")]
    altura = 420

    def figura(self, df):
        df = df.nlargest(TOP_N, "orcamento_atualizado").iloc[::-1]
        nomes = df["nome_orgao_superior"].str.slice(0, 38)
        fig = go.Figure()
        fig.add_bar(y=nomes, x=df["orcamento_atualizado"], name="Atualizado", orientation="h",
                    marker_color=CORES["Atualizado"])
        fig.add_bar(y=nomes, x=df["orcamento_realizado"], name="Realizado", orientation="h",
                    marker_color=CORES["Realizado"])
        fig.update_layout(barmode="group", xaxis_title=UNIDADE, legend=dict(orientation="h", y=1.08))
        return fig
