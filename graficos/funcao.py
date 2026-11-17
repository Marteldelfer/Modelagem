import plotly.express as px

from graficos.base import Grafico


class FuncaoSubfuncao(Grafico):
    id = "g-funcao"
    titulo = "Orçamento atualizado por função e subfunção"
    agrupar_por = [("dim_programa_acao", "nome_funcao")]
    largura = 2
    altura = 480

    def figura(self, df):
        df = df[df["orcamento_atualizado"] > 0].fillna({"nome_funcao": "Sem informação",
                                                        "nome_subfuncao": "Sem informação"})
        fig = px.treemap(df, path=["nome_funcao"], values="orcamento_atualizado")
        fig.update_traces(hovertemplate="%{label}<br>R$ %{value:,.2f} bi<extra></extra>")
        fig.update_layout(font_size=32)
        return fig
