from filtros.base import HierarchicalFilter, Level

programa_acao = HierarchicalFilter(
    prefix="prog",
    title="Programa / Ação",
    table="dim_programa_acao",
    key_col="key_programa",
    levels=[
        Level("funcao", "Função", "codigo_funcao", "nome_funcao"),
        Level("programa", "Programa orçamentário", "codigo_programa_orcamentario", "nome_programa_orcamentario"),
        Level("acao", "Ação", "codigo_acao", "nome_acao"),
    ],
)
