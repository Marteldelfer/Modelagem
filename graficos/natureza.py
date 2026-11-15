import plotly.express as px

from graficos.base import Grafico


class GrupoDespesa(Grafico):
    id = "g-natureza"
    titulo = "Orçamento atualizado por grupo de despesa"
    agrupar_por = [("dim_natureza_despesa", "nome_grupo_despesa")]

    def figura(self, df):
        df = df[df["orcamento_atualizado"] > 0]
        fig = px.pie(df, names="nome_grupo_despesa", values="orcamento_atualizado", hole=0.5)
        fig.update_traces(textinfo="percent", hovertemplate="%{label}<br>R$ %{value:,.2f} bi<extra></extra>")
        fig.update_layout(legend=dict(font=dict(size=10)))
        return fig
