"""Consultas sobre a tabela fato feitas em memória.

A fato é lida uma única vez (via load_dimension: read_sql com fallback para pickle) e
todos os filtros/agregações passam a ser operações de DataFrame.
"""
import json
from functools import lru_cache
import os

import pandas as pd

from data import load_dimension
from sidebar import FILTROS

FATO = "fato_orcamento_despesa"
MEDIDAS = ["orcamento_inicial", "orcamento_atualizado", "orcamento_empenhado", "orcamento_realizado"]
CHAVES = {f.table: f.key_col for f in FILTROS}   # dimensão -> chave na fato


@lru_cache(maxsize=1)
def _fato() -> pd.DataFrame:
    """Lê a fato uma vez. Se o seu data.py tiver outra função genérica de leitura
    (read_sql + read_pickle), use-a aqui no lugar de load_dimension."""
    df = load_dimension(FATO)
    for chave in CHAVES.values():                      # chaves menores = menos memória
        df[chave] = pd.to_numeric(df[chave], downcast="integer")
    return df


def precarregar():
    """Opcional: chame na inicialização do app para a primeira requisição não esperar a leitura."""
    _fato()
    for tabela in CHAVES:
        load_dimension(tabela)


def _validar(tabela: str, coluna: str | None = None):
    if tabela not in CHAVES or (coluna is not None and coluna not in load_dimension(tabela).columns):
        raise ValueError(f"Coluna inválida: {tabela}.{coluna}")


@lru_cache(maxsize=16)
def _filtrada(filtros_json: str) -> pd.DataFrame:
    """Linhas da fato que atendem aos filtros do painel (só leitura: não altere o resultado)."""
    fato = _fato()
    mascara = None
    for tabela, colunas in json.loads(filtros_json).items():
        selecionadas = {c: v for c, v in colunas.items() if v}
        if not selecionadas:
            continue
        _validar(tabela)
        dim = load_dimension(tabela)
        ok = pd.Series(True, index=dim.index)
        for coluna, valores in selecionadas.items():
            _validar(tabela, coluna)
            ok &= dim[coluna].isin(valores)
        parcial = fato[CHAVES[tabela]].isin(dim.loc[ok, CHAVES[tabela]])
        mascara = parcial if mascara is None else mascara & parcial
    return fato if mascara is None else fato[mascara]


def _json(filtros) -> str:
    return json.dumps(filtros or {}, sort_keys=True)


# ---------- agregações para os gráficos ----------
def consultar(agrupar_por, filtros) -> pd.DataFrame:
    """agrupar_por: lista de (dimensão, coluna). Sem agrupamento, devolve uma linha com os totais."""
    return _agregar(tuple(tuple(x) for x in agrupar_por), _json(filtros)).copy()


@lru_cache(maxsize=128)
def _agregar(agrupar_por, filtros_json) -> pd.DataFrame:
    fato = _filtrada(filtros_json)
    if not agrupar_por:
        return pd.DataFrame([fato[MEDIDAS].sum()])

    tabelas = list(dict.fromkeys(t for t, _ in agrupar_por))
    for tabela, coluna in agrupar_por:
        _validar(tabela, coluna)

    # reduz primeiro pelas chaves (poucas combinações), depois traz as colunas das dimensões
    chaves = [CHAVES[t] for t in tabelas]
    df = fato.groupby(chaves, sort=False)[MEDIDAS].sum().reset_index()
    for tabela in tabelas:
        colunas = list(dict.fromkeys(c for t, c in agrupar_por if t == tabela))
        df = df.merge(load_dimension(tabela)[[CHAVES[tabela], *colunas]], on=CHAVES[tabela], how="inner")

    grupos = list(dict.fromkeys(c for _, c in agrupar_por))
    return df.groupby(grupos, dropna=False, as_index=False)[MEDIDAS].sum()


# ---------- exportação (linhas da fato com todas as dimensões) ----------
def contar_linhas(filtros: dict) -> int:
    return len(_filtrada(_json(filtros)))


def detalhar(filtros: dict) -> pd.DataFrame:
    """Linhas da fato com as colunas descritivas das dimensões (sem as chaves key_*)."""
    df = _filtrada(_json(filtros))
    for tabela in sorted(CHAVES):
        df = df.merge(load_dimension(tabela), on=CHAVES[tabela], how="inner")
    colunas = [c for t in sorted(CHAVES) for c in load_dimension(t).columns if c != CHAVES[t]]
    return df[colunas + MEDIDAS].reset_index(drop=True)