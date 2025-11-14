from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import logging
import os

from . import crud, models
from .database import SessionLocal, engine
from sqlalchemy import func, distinct # Importações para queries SQL

# Importações necessárias
from backend.collectors.google_maps_collector import GoogleMapsCollector
from backend.collectors.structured_data_collector import StructuredDataCollector
from backend.collectors.public_opinion_collector import PublicOpinionCollector
# Importa o DataAnalyzer para os endpoints de análise
from backend.collectors.data_analyzer import DataAnalyzer


logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Termômetro do Maranhão API",
    description="API para dados demográficos e de satisfação do estado do Maranhão",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== ENDPOINTS DE ANÁLISE (OTIMIZADOS) ==========

@app.post("/api/data/analysis") # MUDADO PARA POST
def get_data_analysis(filters: Dict[str, Any] = None, db: Session = Depends(get_db)):
    """
    Retorna análise completa dos dados coletados.
    Agora aceita um corpo POST com filtros.
    *** OTIMIZADO: Roda direto no SQL ***
    """
    try:
        logger.info(f"=== INICIANDO ANÁLISE (Filtros: {filters}) ===")
        
        analyzer = DataAnalyzer(db)
        # A análise agora é feita 100% no SQL
        analysis, _ = analyzer.analyze_dataset(filters) 
        
        if analysis.get('total_records', 0) == 0:
            logger.warning("DataFrame vazio após filtros!")
            return {
                "status": "success", 
                "message": "Nenhum dado disponível para os filtros aplicados",
                "analysis": analysis # Retorna análise vazia
            }
        
        logger.info(f"Análise concluída: {analysis.get('total_records', 0)} registros")
        
        return {
            "status": "success",
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"ERRO CRÍTICO na análise: {e}", exc_info=True)
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}

@app.post("/api/data/comparison-tables") # MUDADO PARA POST
def get_comparison_tables(filters: Dict[str, Any] = None, db: Session = Depends(get_db)):
    """
    Retorna tabelas comparativas dos dados.
    Agora aceita um corpo POST com filtros.
    *** OTIMIZADO: Roda direto no SQL ***
    """
    try:
        logger.info(f"=== GERANDO TABELAS (Filtros: {filters}) ===")
        
        analyzer = DataAnalyzer(db)
        # As tabelas agora são geradas 100% no SQL
        tables = analyzer.generate_comparison_tables(filters)

        if not tables.get('source_comparison'):
             logger.warning("Nenhum dado para tabelas!")
        
        logger.info("Tabelas geradas com sucesso")
        
        return {
            "status": "success",
            "tables": tables,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Erro ao gerar tabelas: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


@app.post("/api/data/filter")
def filter_data(filters: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Filtra dados baseado em critérios fornecidos.
    *** OTIMIZADO: Roda direto no SQL ***
    """
    try:
        analyzer = DataAnalyzer(db)
        
        # 1. Busca os dados brutos filtrados e paginados
        data, total_count = analyzer.get_filtered_data_paginated(filters, skip=0, limit=1000)
        
        if not data:
            return {"status": "success", "total": 0, "data": [], "filters_applied": filters}
        
        # 2. Converte os objetos SQLAlchemy para dicts
        records = []
        for m in data:
            records.append({
                'id': m.id,
                'source_platform': m.source_platform,
                'theme': m.theme,
                'text': m.text,
                'sentiment': m.sentiment,
                'location': m.location,
                'timestamp_utc': m.timestamp_utc.isoformat() if m.timestamp_utc else None,
                'quality_score': m.quality_score,
                'issues': m.issues,
                'reliability': m.reliability
            })
        
        return {
            "status": "success",
            "total": total_count, # Retorna o total de registros (sem paginação)
            "data": records,     # Retorna apenas a primeira página (1000)
            "filters_applied": filters
        }
    
    except Exception as e:
        logger.error(f"Erro ao filtrar dados: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}

@app.get("/api/data/filters/options")
def get_filter_options(db: Session = Depends(get_db)):
    """Retorna opções disponíveis para filtros."""
    try:
        themes = db.query(distinct(models.Mention.theme)).filter(
            models.Mention.theme.isnot(None)
        ).all()
        
        locations = db.query(distinct(models.Mention.location)).filter(
            models.Mention.location.isnot(None)
        ).all()
        
        sources = db.query(distinct(models.Mention.source_platform)).filter(
            models.Mention.source_platform.isnot(None)
        ).all()
        
        sentiments = db.query(distinct(models.Mention.sentiment)).filter(
            models.Mention.sentiment.isnot(None)
        ).all()
        
        return {
            "status": "success",
            "options": {
                "themes": sorted([t[0] for t in themes if t[0]]),
                "locations": sorted([l[0] for l in locations if l[0]]),
                "sources": sorted([s[0] for s in sources if s[0]]),
                "sentiments": sorted([s[0] for s in sentiments if s[0]]),
                "reliability_levels": ["high", "medium", "low"]
            }
        }
    
    except Exception as e:
        logger.error(f"Erro ao buscar opções de filtro: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}

# ========== ENDPOINTS DO INDEX.HTML (MAPA) ==========

@app.get("/api/data")
def read_data(db: Session = Depends(get_db), 
                theme: str = Query(None), 
                location: str = Query(None), 
                search_text: str = Query(None)):
    """
    Retorna as menções mais recentes, com filtros.
    Otimizado para o index.html (mapa).
    """
    # Usa a função de crud atualizada com filtros
    # O limite de 100 é para a carga inicial/filtrada (super rápido)
    limit = 100
    
    return crud.get_mentions(db, limit=limit, 
                             theme=theme, 
                             location=location, 
                             search_text=search_text)

@app.get("/api/data/{city_name}")
def read_city_data(city_name: str, db: Session = Depends(get_db)):
    """Retorna dados para uma cidade específica."""
    return crud.get_mentions_by_city(db, city=city_name)

@app.get("/api/scores")
def get_city_scores(db: Session = Depends(get_db)):
    """Retorna scores de satisfação por cidade (baseado em TODOS os dados)."""
    logger.info("Calculando scores do mapa...")
    
    # Query SQL otimizada para contar apenas menções negativas por cidade
    stmt = db.query(
        models.Mention.location,
        func.count(models.Mention.id)
    ).filter(
        models.Mention.sentiment == 'NEGATIVO',
        models.Mention.location.isnot(None),
        models.Mention.location != "Maranhão"
    ).group_by(models.Mention.location)
    
    scores = {location: count for location, count in stmt.all()}
    
    logger.info(f"Scores do mapa calculados para {len(scores)} cidades.")
    return scores

# ... (outros endpoints como /api/cities, /api/stats/summary, /) ...
@app.get("/api/cities")
def get_available_cities(db: Session = Depends(get_db)):
    """Retorna lista de todas as cidades com dados disponíveis."""
    try:
        cities_query = db.query(models.Mention.location, func.count(models.Mention.id).label('total')).filter(
            models.Mention.location.isnot(None),
            models.Mention.location != "Maranhão"
        ).group_by(models.Mention.location).order_by(models.Mention.location).all()
        
        cities_with_counts = []
        for city, count in cities_query:
            cities_with_counts.append({
                'name': city,
                'total_mentions': count
                # 'has_demographics' foi removido para acelerar a query
            })
        
        return {
            'total_cities': len(cities_with_counts),
            'cities': cities_with_counts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cidades: {str(e)}")

@app.get("/api/stats/summary")
def get_database_summary(db: Session = Depends(get_db)):
    """Retorna estatísticas gerais do banco de dados (OTIMIZADO)."""
    try:
        # Roda todas as contagens em paralelo se possível (aqui são sequenciais)
        total_mentions = db.query(models.Mention).count()
        
        stats = {
            'total_records': total_mentions,
            'by_sentiment': {row[0] or 'Unknown': row[1] for row in db.query(models.Mention.sentiment, func.count(models.Mention.id)).group_by(models.Mention.sentiment).all()},
            'by_theme': {row[0] or 'Unknown': row[1] for row in db.query(models.Mention.theme, func.count(models.Mention.id)).group_by(models.Mention.theme).all()},
            'by_source': {row[0] or 'Unknown': row[1] for row in db.query(models.Mention.source_platform, func.count(models.Mention.id)).group_by(models.Mention.source_platform).all()},
            'by_location': {row[0]: row[1] for row in db.query(models.Mention.location, func.count(models.Mention.id)).filter(models.Mention.location.isnot(None), models.Mention.location != "Maranhão").group_by(models.Mention.location).order_by(func.count(models.Mention.id).desc()).limit(10).all()},
            'date_range': {}
        }
        
        date_stats = db.query(func.min(models.Mention.timestamp_utc), func.max(models.Mention.timestamp_utc)).first()
        stats['date_range']['earliest'] = date_stats[0].isoformat() if date_stats[0] else None
        stats['date_range']['latest'] = date_stats[1].isoformat() if date_stats[1] else None
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar estatísticas: {str(e)}")
        
@app.post("/api/data/report") # ATUALIZADO PARA POST
def get_analysis_report(filters: Dict[str, Any] = None, db: Session = Depends(get_db)):
    """Retorna relatório de análise em texto (agora aceita filtros)."""
    try:
        analyzer = DataAnalyzer(db)
        analysis, _ = analyzer.analyze_dataset(filters) # Gera análise com filtros
        
        if analysis.get('total_records', 0) == 0:
            return {"status": "success", "report": "Nenhum dado encontrado para os filtros aplicados."}

        report = analyzer.export_analysis_report(analysis) # Passa a análise
        
        return {
            "status": "success",
            "report": report,
            "format": "text/plain"
        }
    
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}

@app.get("/")
def read_root():
    """Endpoint raiz com informações da API."""
    return {
        "message": "Termômetro do Maranhão API v2.0",
        "description": "API para dados demográficos e de satisfação do estado do Maranhão",
        "endpoints": {
            "/api/data": "Todas as menções",
            "/api/data/{city}": "Dados de uma cidade específica",
            "/api/scores": "Scores de satisfação por cidade",
            "/api/cities": "Lista de cidades disponíveis",
            "/api/stats/summary": "Estatísticas gerais do sistema",
            "/api/data/analysis": "Análise completa com qualidade de dados (aceita POST com filtros)",
            "/api/data/filter": "Filtrar dados com critérios avançados (aceita POST com filtros)",
            "/api/data/comparison-tables": "Tabelas comparativas de dados (aceita POST com filtros)",
            "/api/data/report": "Relatório textual de análise (aceita POST com filtros)",
            "/api/data/filters/options": "Opções disponíveis para filtros"
        },
        "data_sources": [
            "IBGE - Instituto Brasileiro de Geografia e Estatística",
            "INEP - Instituto Nacional de Estudos e Pesquisas Educacionais",
            "Ministério da Saúde - CNES",
            "Portais de notícias locais",
            "Redes sociais e opinião pública",
            "Google Maps"
        ]
    }

# Endpoint de População (movido para o final, pois é menos usado)
@app.post("/api/data/populate")
def populate_database(db: Session = Depends(get_db)):
    """
    Coleta dados de todas as fontes e salva no banco.
    ATENÇÃO: Este endpoint recria o banco de dados.
    """
    try:
        logger.info("=== INICIANDO POPULAÇÃO DO BANCO DE DADOS ===")
        
        # (Chama o script run_collectors em um subprocesso - forma mais segura)
        # Esta é uma implementação mais robusta
        import subprocess
        
        logger.info("Recriando banco e iniciando run_collectors.py...")
        # Encontra o executável python
        python_executable = sys.executable 
        
        # Roda o script e espera terminar
        process = subprocess.Popen(
            [python_executable, "run_collectors.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("População via run_collectors.py finalizada com sucesso.")
            return {
                "status": "success", 
                "message": "Banco de dados recriado e populado com sucesso.",
                "log": stdout
            }
        else:
            logger.error(f"Erro ao executar run_collectors.py: {stderr}")
            raise Exception(f"Erro no subprocesso: {stderr}")

    except Exception as e:
        logger.error(f"ERRO CRÍTICO no endpoint de população: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}