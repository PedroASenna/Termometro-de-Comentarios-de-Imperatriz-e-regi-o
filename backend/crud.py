from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from . import models
from datetime import datetime
import random

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

def get_mentions(db: Session, skip: int = 0, limit: int = 200,
                   theme: str = None,
                   location: str = None,
                   search_text: str = None):
    """
    Retorna menções BALANCEADAS, ordenadas pela data mais recente e com filtros SQL.

    NOVO: Implementa distribuição balanceada entre:
    - Fontes de dados (todas as 8 fontes)
    - Sentimentos (positivo, negativo, neutro)
    - Cidades (diversas cidades do Maranhão)
    """

    # ===== ESTRATÉGIA DE BALANCEAMENTO =====
    # 1. Buscar fontes disponíveis no banco
    available_sources = db.query(distinct(models.Mention.source_platform)).filter(
        models.Mention.source_platform.isnot(None)
    ).all()
    available_sources = [s[0] for s in available_sources if s[0]]

    if not available_sources:
        # Fallback: retorna vazio se não houver dados
        return []

    # 2. Calcular quantas menções buscar por fonte
    mentions_per_source = max(1, limit // len(available_sources))

    # 3. Para cada fonte, buscar menções balanceadas entre sentimentos
    all_mentions = []

    for source in available_sources:
        # Query base para esta fonte
        source_query = db.query(models.Mention).filter(
            models.Mention.source_platform == source
        )

        # Aplica filtros do usuário
        if theme and theme != 'Todos':
            source_query = source_query.filter(models.Mention.theme == theme)

        if location and location != 'Todos':
            source_query = source_query.filter(models.Mention.location == location)

        if search_text:
            source_query = source_query.filter(models.Mention.text.ilike(f"%{search_text}%"))

        # Busca balanceando entre sentimentos (40% positivo, 40% negativo, 20% neutro)
        mentions_per_sentiment = {
            'POSITIVO': int(mentions_per_source * 0.40),
            'NEGATIVO': int(mentions_per_source * 0.40),
            'NEUTRO': int(mentions_per_source * 0.20)
        }

        for sentiment, qty in mentions_per_sentiment.items():
            sentiment_mentions = source_query.filter(
                models.Mention.sentiment == sentiment
            ).order_by(
                func.random()  # Randomiza para variar as cidades
            ).limit(qty).all()

            all_mentions.extend(sentiment_mentions)

    # 4. Se não atingiu o limite, complementa com dados aleatórios
    if len(all_mentions) < limit:
        remaining = limit - len(all_mentions)

        # Query para pegar o restante
        extra_query = db.query(models.Mention)

        # Aplica filtros
        if theme and theme != 'Todos':
            extra_query = extra_query.filter(models.Mention.theme == theme)

        if location and location != 'Todos':
            extra_query = extra_query.filter(models.Mention.location == location)

        if search_text:
            extra_query = extra_query.filter(models.Mention.text.ilike(f"%{search_text}%"))

        # Exclui IDs já selecionados
        selected_ids = [m.id for m in all_mentions]
        if selected_ids:
            extra_query = extra_query.filter(models.Mention.id.notin_(selected_ids))

        extra_mentions = extra_query.order_by(func.random()).limit(remaining).all()
        all_mentions.extend(extra_mentions)

    # 5. Embaralha para não ficar agrupado por fonte
    random.shuffle(all_mentions)

    # 6. Ordena por data (mais recentes primeiro) e aplica skip/limit final
    all_mentions.sort(key=lambda x: x.timestamp_utc if x.timestamp_utc else datetime.min, reverse=True)

    return all_mentions[skip:skip+limit] if skip else all_mentions[:limit]

def get_mentions_by_city(db: Session, city: str):
    # Mantém a ordenação por data
    return db.query(models.Mention)\
             .filter(models.Mention.location == city)\
             .order_by(models.Mention.timestamp_utc.desc())\
             .all()