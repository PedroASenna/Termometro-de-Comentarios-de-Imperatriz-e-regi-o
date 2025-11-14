from sqlalchemy.orm import Session
from . import models
from datetime import datetime

def create_mention(db: Session, mention_data: dict):
    db_mention = models.Mention(
        source_platform=mention_data.get('source_platform'),
        theme=mention_data.get('theme'),
        text=mention_data.get('text'),
        sentiment=mention_data.get('sentiment'),
        location=mention_data.get('location'),
        timestamp_utc=mention_data.get('timestamp_utc', datetime.utcnow()),
        url=mention_data.get('url'),
        
        # NOVOS CAMPOS:
        indicator_id=mention_data.get('indicator_id'),
        indicator_name=mention_data.get('indicator_name'),
        indicator_value=mention_data.get('indicator_value'),
        indicator_unit=mention_data.get('indicator_unit'),
        indicator_year=mention_data.get('indicator_year'),
        
        # *** SALVANDO DADOS DE QUALIDADE PRÉ-CALCULADOS ***
        quality_score=mention_data.get('quality_score'),
        issues=mention_data.get('issues'),
        reliability=mention_data.get('reliability')
    )
    db.add(db_mention)
    # Commit será feito em lote pelo run_collectors.py
    # db.commit() 
    # db.refresh(db_mention)
    return db_mention

def get_mentions(db: Session, skip: int = 0, limit: int = 100, 
                   theme: str = None, 
                   location: str = None, 
                   search_text: str = None):
    """
    Retorna menções, ordenadas pela data mais recente e com filtros SQL.
    """
    
    # Inicia a query base
    query = db.query(models.Mention)
    
    # Aplica filtros se eles existirem
    if theme and theme != 'Todos':
        query = query.filter(models.Mention.theme == theme)
    
    if location and location != 'Todos':
        query = query.filter(models.Mention.location == location)
        
    if search_text:
        # Usa 'ilike' para busca case-insensitive
        query = query.filter(models.Mention.text.ilike(f"%{search_text}%"))

    # Aplica ordenação, skip e limit no final
    return query.order_by(models.Mention.timestamp_utc.desc())\
                .offset(skip)\
                .limit(limit)\
                .all()

def get_mentions_by_city(db: Session, city: str):
    # Mantém a ordenação por data
    return db.query(models.Mention)\
             .filter(models.Mention.location == city)\
             .order_by(models.Mention.timestamp_utc.desc())\
             .all()