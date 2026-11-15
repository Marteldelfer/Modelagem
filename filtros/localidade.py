from filtros.base import HierarchicalFilter, Level

localidade = HierarchicalFilter(
    prefix="loc",
    title="Localidade",
    table="dim_localidade",
    key_col="key_localidade",
    levels=[
        Level("nacionalidade", "Nacionalidade", "nacionalidade"),
        Level("regiao", "Região", "regiao"),
        Level("uf", "UF", "uf")
    ],
)
