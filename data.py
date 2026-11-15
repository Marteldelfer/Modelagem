"""Acesso ao DataWarehouse. Ajuste apenas a string de conexão (variável DW_URL)."""
import os
from functools import lru_cache

import pandas as pd
from sqlalchemy import create_engine


MYSQL_USER = os.getenv("DW_MYSQL_USER", "root")          # Usuário padrão do MySQL
MYSQL_PASS = os.getenv("DW_MYSQL_PASS", "pass")      # Senha configurada na instalação do MySQL
MYSQL_HOST = os.getenv("DW_MYSQL_HOST", "localhost")     # Servidor local (localhost ou IP da nuvem)
MYSQL_PORT = os.getenv("DW_MYSQL_PORT", "3306")          # Porta padrão do serviço MySQL Server
MYSQL_DB   = os.getenv("DW_MYSQL_DB", "dw_orcamento")    # Nome do esquema do Data Warehouse

DW_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"


@lru_cache(maxsize=1)
def get_engine():
    return create_engine(DW_URL)


@lru_cache(maxsize=None)
def load_dimension(table: str) -> pd.DataFrame:
    """Carrega uma dimensão inteira (dimensões costumam ser pequenas) e mantém em cache."""
    return pd.read_sql(f"SELECT * FROM {table}", get_engine())
