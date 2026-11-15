from filtros.base import HierarchicalFilter, Level

natureza_despesa = HierarchicalFilter(
    prefix="nat",
    title="Natureza da despesa",
    table="dim_natureza_despesa",
    key_col="key_natureza_despesa",
    levels=[
        Level("categoria", "Categoria econômica", "codigo_categoria_economica", "nome_categoria_economica"),
        Level("grupo", "Grupo de despesa", "codigo_grupo_despesa", "nome_grupo_despesa"),
        Level("elemento", "Elemento de despesa", "codigo_elemento_despesa", "nome_elemento_despesa"),
    ],
)
