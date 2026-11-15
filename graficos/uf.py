import plotly.express as px

from graficos.base import UNIDADE, Grafico


class PorUF(Grafico):
    id = "g-uf"
    titulo = "Orçamento atualizado por UF"
    agrupar_por = [("dim_localidade", "uf"), ("dim_localidade", "regiao")]
    largura = 2

    def figura(self, df):
        df = df.dropna(subset=["uf"]).sort_values("orcamento_atualizado", ascending=False)
        fig = px.bar(df, x="uf", y="orcamento_atualizado", color="regiao",
                     labels={"orcamento_atualizado": UNIDADE, "uf": ""})
        fig.update_xaxes(categoryorder="total descending")
        fig.update_traces(hovertemplate="%{x}: R$ %{y:,.2f} bi<extra></extra>")
        return fig
