"""Consultas na tabela fato, aplicando os filtros do painel lateral.

As colunas filtradas/agrupadas são validadas contra as dimensões (lista fechada) e os
valores vão como parâmetros, então o conteúdo do dcc.Store não vira SQL.
"""
import json
from functools import lru_cache

import pandas as pd
from sqlalchemy import bindparam, text

from data import get_engine, load_dimension
from sidebar import FILTROS

FATO = "fato_orcamento_despesa"
MEDIDAS = ["orcamento_inicial", "orcamento_atualizado", "orcamento_empenhado", "orcamento_realizado"]
CHAVES = {f.table: f.key_col for f in FILTROS}   # dimensão -> chave na fato


def _q(nome: str) -> str:
    return get_engine().dialect.identifier_preparer.quote(nome)


def _ref(tabela: str, coluna: str) -> str:
    if tabela not in CHAVES or coluna not in load_dimension(tabela).columns:
        raise ValueError(f"Coluna inválida: {tabela}.{coluna}")
    return f"{_q(tabela)}.{_q(coluna)}"


def _joins(tabelas) -> str:
    return " ".join(
        f"JOIN {_q(t)} ON {_q(t)}.{_q(CHAVES[t])} = f.{_q(CHAVES[t])}" for t in sorted(tabelas)
    )


def _filtrar(filtros: dict):
    """Filtros do painel -> (dimensões usadas, cláusulas WHERE, parâmetros)."""
    tabelas, where, params = set(), [], {}
    for tabela, colunas in (filtros or {}).items():
        for coluna, valores in colunas.items():
            if not valores:
                continue
            nome = f"p{len(params)}"
            where.append(f"{_ref(tabela, coluna)} IN :{nome}")
            params[nome] = valores
            tabelas.add(tabela)
    return tabelas, where, params


def _executar(sql: str, params: dict) -> pd.DataFrame:
    stmt = text(sql).bindparams(*[bindparam(n, expanding=True) for n in params])
    return pd.read_sql(stmt, get_engine(), params=params)


# ---------- agregações para os gráficos ----------
def consultar(agrupar_por, filtros) -> pd.DataFrame:
    """agrupar_por: lista de (dimensão, coluna). Sem agrupamento, devolve uma linha com os totais."""
    chave = tuple(tuple(x) for x in agrupar_por)
    return _consultar(chave, json.dumps(filtros or {}, sort_keys=True)).copy()


@lru_cache(maxsize=128)
def _consultar(agrupar_por, filtros_json) -> pd.DataFrame:
    tabelas, where, params = _filtrar(json.loads(filtros_json))

    selecao = []
    for tabela, coluna in agrupar_por:
        selecao.append(f"{_ref(tabela, coluna)} AS {_q(coluna)}")
        tabelas.add(tabela)

    medidas = ", ".join(f"SUM(f.{_q(m)}) AS {_q(m)}" for m in MEDIDAS)
    sql = f"SELECT {', '.join(selecao + [medidas])} FROM {_q(FATO)} f {_joins(tabelas)}"
    if where:
        sql += " WHERE " + " AND ".join(where)
    if selecao:
        sql += " GROUP BY " + ", ".join(_ref(t, c) for t, c in agrupar_por)

    df = _executar(sql, params)
    df[MEDIDAS] = df[MEDIDAS].fillna(0)
    return df


# ---------- exportação (linhas da fato com todas as dimensões) ----------
def _from_where(filtros: dict):
    _, where, params = _filtrar(filtros)
    sql = f"FROM {_q(FATO)} f {_joins(CHAVES)}"   # todas as dimensões
    if where:
        sql += " WHERE " + " AND ".join(where)
    return sql, params


def contar_linhas(filtros: dict) -> int:
    sql, params = _from_where(filtros)
    return int(_executar(f"SELECT COUNT(*) AS n {sql}", params)["n"].iloc[0])


def detalhar(filtros: dict) -> pd.DataFrame:
    """Linhas da fato já com as colunas descritivas das dimensões (sem as chaves key_*)."""
    colunas = [(t, c) for t in sorted(CHAVES) for c in load_dimension(t).columns if c != CHAVES[t]]
    selecao = [f"{_ref(t, c)} AS {_q(c)}" for t, c in colunas] + [f"f.{_q(m)}" for m in MEDIDAS]
    sql, params = _from_where(filtros)
    return _executar(f"SELECT {', '.join(selecao)} {sql}", params)