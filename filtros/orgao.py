from filtros.base import HierarchicalFilter, Level

orgao = HierarchicalFilter(
    prefix="org",
    title="Órgão",
    table="dim_orgao",
    key_col="key_orgao",
    levels=[
        Level("superior", "Órgão superior", "codigo_orgao_superior", "nome_orgao_superior"),
        Level("subordinado", "Órgão subordinado", "codigo_orgao_subordinado", "nome_orgao_subordinado"),
        Level("unidade", "Unidade orçamentária", "codigo_unidade_orcamentaria", "nome_unidade_orcamentaria"),
    ],
)
