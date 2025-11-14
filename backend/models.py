# No arquivo: backend/models.py

# Importações limpas
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Index
from sqlalchemy.orm import relationship
from .database import Base

class Mention(Base):
    __tablename__ = "mentions"

    id = Column(Integer, primary_key=True, index=True)
    source_platform = Column(String, index=True)
    theme = Column(String, index=True)
    text = Column(Text)
    sentiment = Column(String, index=True)
    location = Column(String, index=True)
    timestamp_utc = Column(DateTime, index=True) # Adicionado index=True para performance
    url = Column(String)

    
    # NOVAS COLUNAS PARA DADOS NUMÉRICOS
    indicator_id = Column(String, index=True)    # ID do indicador (ex: '29171')
    indicator_name = Column(String)              # Nome do indicador (ex: 'População estimada')
    indicator_value = Column(Float)              # Valor numérico (População, PIB, etc.)
    indicator_unit = Column(String)              # Unidade (ex: 'pessoas', 'R$')
    indicator_year = Column(String)              # Ano de referência (ex: '2023')
    
    # *** NOVAS COLUNAS DE QUALIDADE (PRÉ-CALCULADAS) ***
    quality_score = Column(Integer, index=True)  # Score de 0 a 100
    issues = Column(Text)                        # String com problemas (ex: "Texto curto, Data inválida")
    reliability = Column(String, index=True)     # 'high', 'medium', 'low'

# Adiciona um índice composto para acelerar as consultas mais comuns
Index('idx_theme_location_sentiment', Mention.theme, Mention.location, Mention.sentiment)