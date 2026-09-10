
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Carrega variáveis do arquivo .env na raiz do projeto (se existir)
load_dotenv()

# URL do banco de dados. Pode ser sobrescrita via variável de ambiente
# DATABASE_URL (ex.: no arquivo .env). Por padrão usa SQLite local.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./termometro_ma.db")

# connect_args só é necessário/suportado para SQLite
_connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

# Criar engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=_connect_args
)

# Criar SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def init_db():
    """Cria todas as tabelas no banco de dados, caso ainda não existam."""
    from . import models  # import local evita ciclo de importação
    Base.metadata.create_all(bind=engine)
