"""
DATA ANALYZER - TERMÔMETRO DO MARANHÃO (VERSÃO OTIMIZADA)
Análise robusta com tratamento completo de erros
*** OTIMIZADO PARA RODAR CONSULTAS SQL DIRETAS ***
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
from backend.models import Mention
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, case

def convert_to_native_types(obj):
    """Converte tipos numpy/pandas para tipos nativos Python."""
    import numpy as np
    
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_native_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    else:
        return obj

logger = logging.getLogger(__name__)

class DataAnalyzer:
    def __init__(self, db_session: Session):
        self.db = db_session
        
        self.quality_criteria = {
            'completeness': 0.8,
            'freshness_days': 30,
            'min_text_length': 20,
            'valid_sentiment': ['POSITIVO', 'NEGATIVO', 'NEUTRO']
        }
        
        self.source_reliability = {
            'high': ['IBGE_Oficial', 'IBGE_Demografia', 'IBGE', 'FBSP'],
            'medium': ['news_', 'reclame_aqui', 'google_reviews', 'Google Maps', 'Reclame Aqui', 'Procon/MP-MA', 'DATASUS', 'INEP', 'Portal da Transparência', 'FBSP'],
            'low': ['social_', 'comment_']
        }

    def _build_filtered_query(self, filters: Dict[str, Any] = None):
        """
        Constrói uma query SQLAlchemy base com todos os filtros aplicados.
        Esta é a base de toda a otimização.
        """
        query = self.db.query(Mention)
        if not filters:
            return query
            
        logger.info(f"Construindo query com filtros: {filters}")

        # Filtros SQL diretos
        if filters.get('source'):
            query = query.filter(Mention.source_platform.ilike(f"%{filters['source']}%"))
        if filters.get('theme') and filters['theme'] != 'Todos':
            query = query.filter(Mention.theme == filters['theme'])
        if filters.get('location') and filters['location'] != 'Todos':
            query = query.filter(Mention.location == filters['location'])
        if filters.get('sentiment') and filters['sentiment'] != 'Todos':
            query = query.filter(Mention.sentiment == filters['sentiment'])
        if filters.get('date_from'):
            try: query = query.filter(Mention.timestamp_utc >= pd.to_datetime(filters['date_from']))
            except: pass
        if filters.get('date_to'):
            try: query = query.filter(Mention.timestamp_utc <= pd.to_datetime(filters['date_to']))
            except: pass
        if filters.get('search_text'):
            query = query.filter(Mention.text.ilike(f"%{filters['search_text']}%"))
            
        # Filtros de campos pré-calculados
        if filters.get('reliability') and filters['reliability'] != 'Todos':
            query = query.filter(Mention.reliability == filters['reliability'])
        if filters.get('min_quality') and filters.get('min_quality') != '0':
            query = query.filter(Mention.quality_score >= int(filters['min_quality']))
            
        return query

    def get_filtered_data_paginated(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 1000) -> (List[Mention], int):
        """
        Busca dados brutos paginados, JÁ FILTRADOS.
        """
        query = self._build_filtered_query(filters)
        
        # Conta o total *antes* de paginar
        total_count = query.count()
        
        # Aplica paginação e ordenação
        data = query.order_by(Mention.timestamp_utc.desc()).offset(skip).limit(limit).all()
        
        return data, total_count


    def calculate_data_quality_score(self, record: dict) -> Dict[str, Any]:
        """
        Calcula score de qualidade para um *dicionário* de registro.
        Otimizado para ser usado pelo run_collectors.py.
        """
        score = 100
        issues = []
        
        try:
            # 1. Completude
            required_fields = ['source_platform', 'theme', 'text', 'sentiment', 'location']
            missing = [f for f in required_fields if not record.get(f) or str(record.get(f)).strip() == '']
            
            if missing:
                score -= len(missing) * 10
                issues.append(f"Campos vazios: {', '.join(missing)}")
            
            # 2. Atualidade
            try:
                # Tenta normalizar o timestamp que pode ser string ou datetime
                timestamp = record.get('timestamp_utc')
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif not isinstance(timestamp, datetime):
                    timestamp = datetime.utcnow()
                    
                days_old = (datetime.utcnow() - timestamp).days
                if days_old > self.quality_criteria['freshness_days']:
                    score -= 15
                    issues.append(f"Dados antigos ({days_old} dias)")
            except:
                score -= 20
                issues.append("Data inválida")
            
            # 3. Tamanho do texto
            text_len = len(str(record.get('text', '')))
            if text_len < self.quality_criteria['min_text_length']:
                score -= 10
                issues.append(f"Texto curto ({text_len} chars)")
            
            # 4. Sentimento válido
            if record.get('sentiment') not in self.quality_criteria['valid_sentiment']:
                score -= 10
                issues.append("Sentimento inválido")
            
            # 5. URL válida
            url = str(record.get('url', ''))
            if url and not url.startswith('http'): # Permite URL vazia
                score -= 5
                issues.append("URL inválida")
            
            # 6. Confiabilidade
            source = str(record.get('source_platform', ''))
            reliability = self.get_source_reliability(source)
            
            if reliability == 'low':
                score -= 10
            elif reliability == 'high':
                score += 10 # Bônus para fontes oficiais
            
            return {
                'quality_score': max(0, min(100, score)),
                'issues': ', '.join(issues) if issues else "Nenhum problema",
                'reliability': reliability
            }
        
        except Exception as e:
            logger.error(f"Erro ao calcular qualidade: {e}")
            return {
                'quality_score': 50,
                'issues': 'Erro no cálculo',
                'reliability': 'medium'
            }
    
    def get_source_reliability(self, source: str) -> str:
        """Determina confiabilidade da fonte."""
        try:
            source_lower = source.lower()
            
            for level, patterns in self.source_reliability.items():
                for pattern in patterns:
                    if pattern.lower() in source_lower:
                        return level
            
            return 'medium'
        except:
            return 'medium'
    
    def analyze_dataset(self, filters: Dict[str, Any] = None) -> tuple:
        """Análise completa do dataset (AGORA RODA EM SQL)."""
        
        try:
            # 1. Constrói a query base filtrada
            query = self._build_filtered_query(filters)
            
            # 2. Executa todas as agregações (SQL faz todo o trabalho)
            logger.info("Executando agregações SQL para análise...")
            
            # Total de Registros
            total_records = query.count()
            if total_records == 0:
                logger.warning("Nenhum dado encontrado para analisar.")
                return {'total_records': 0, 'quality_metrics': {}, 'by_source': [], 'by_theme': [], 'by_location': [], 'by_sentiment': {}, 'by_reliability': {}}, pd.DataFrame()

            # Métricas de Qualidade
            quality_stats = query.with_entities(
                func.avg(Mention.quality_score),
                func.sum(case((Mention.quality_score >= 80, 1), else_=0)),
                func.sum(case(((Mention.quality_score >= 50) & (Mention.quality_score < 80), 1), else_=0)),
                func.sum(case((Mention.quality_score < 50, 1), else_=0))
            ).first()

            # Range de Datas
            date_stats = query.with_entities(
                func.min(Mention.timestamp_utc),
                func.max(Mention.timestamp_utc)
            ).first()
            date_start, date_end = date_stats

            analysis = {
                'total_records': total_records,
                'date_range': {
                    'start': date_start.isoformat() if date_start else None,
                    'end': date_end.isoformat() if date_end else None
                },
                'quality_metrics': {
                    'average_score': round(quality_stats[0] or 0, 2),
                    'high_quality_count': int(quality_stats[1] or 0),
                    'medium_quality_count': int(quality_stats[2] or 0),
                    'low_quality_count': int(quality_stats[3] or 0)
                },
                # Funções de análise agora rodam SQL
                'by_source': self._analyze_by_source_sql(query),
                'by_theme': self._analyze_by_theme_sql(query),
                'by_location': self._analyze_by_location_sql(query),
                'by_sentiment': self._analyze_by_sentiment_sql(query),
                'by_reliability': self._analyze_by_reliability_sql(query)
            }
            
            logger.info("✅ Análise SQL concluída.")
            # Retornamos um DF vazio pois não precisamos mais dele no main.py
            return analysis, pd.DataFrame() 
            
        except Exception as e:
            logger.error(f"Erro na análise do dataset: {e}", exc_info=True)
            return {'error': str(e), 'total_records': 0}, pd.DataFrame()

    # --- NOVAS FUNÇÕES DE ANÁLISE BASEADAS EM SQL ---

    def _analyze_by_source_sql(self, query) -> List[Dict]:
        """Análise por fonte (SQL)."""
        try:
            stmt = query.group_by(Mention.source_platform).with_entities(
                Mention.source_platform,
                func.count(Mention.id).label('total'),
                func.avg(Mention.quality_score).label('avg_quality'),
                func.min(Mention.quality_score).label('min_quality'),
                func.max(Mention.quality_score).label('max_quality'),
                func.sum(case((Mention.sentiment == 'POSITIVO', 1), else_=0)).label('positive_count'),
                func.sum(case((Mention.sentiment == 'NEGATIVO', 1), else_=0)).label('negative_count'),
                func.sum(case((Mention.sentiment == 'NEUTRO', 1), else_=0)).label('neutral_count'), # <-- ADICIONADO
                func.max(Mention.reliability).label('reliability') # Pega um valor (todos devem ser iguais)
            ).order_by(func.count(Mention.id).desc())
            
            results = []
            for row in stmt.all():
                total = row.total
                results.append({
                    'source': row.source_platform,
                    'total': total,
                    'avg_quality': round(row.avg_quality or 0, 1),
                    'min_quality': round(row.min_quality or 0, 1),
                    'max_quality': round(row.max_quality or 0, 1),
                    'positive_rate': round((row.positive_count / total * 100), 1) if total > 0 else 0,
                    'negative_rate': round((row.negative_count / total * 100), 1) if total > 0 else 0,
                    'neutral_rate': round((row.neutral_count / total * 100), 1) if total > 0 else 0, # <-- ADICIONADO
                    'reliability': row.reliability or 'medium'
                })
            return results
        except Exception as e:
            logger.error(f"Erro em _analyze_by_source_sql: {e}")
            return []

    def _analyze_by_theme_sql(self, query) -> List[Dict]:
        """Análise por tema (SQL)."""
        try:
            stmt = query.group_by(Mention.theme).with_entities(
                Mention.theme,
                func.count(Mention.id).label('count'),
                func.avg(Mention.quality_score).label('avg_quality'),
                func.sum(case((Mention.sentiment == 'POSITIVO', 1), else_=0)).label('positive'),
                func.sum(case((Mention.sentiment == 'NEGATIVO', 1), else_=0)).label('negative'),
                func.sum(case((Mention.sentiment == 'NEUTRO', 1), else_=0)).label('neutral'),
                func.count(distinct(Mention.source_platform)).label('sources_count')
            ).order_by(func.count(Mention.id).desc())

            results = []
            for row in stmt.all():
                total = row.count
                results.append({
                    'theme': row.theme or 'Outros',
                    'count': total,
                    'avg_quality': round(row.avg_quality or 0, 2),
                    'positive': row.positive,
                    'negative': row.negative,
                    'neutral': row.neutral,
                    'sources_count': row.sources_count,
                    'sentiment_balance': round(((row.positive - row.negative) / total * 100), 1) if total > 0 else 0
                })
            return results
        except Exception as e:
            logger.error(f"Erro em _analyze_by_theme_sql: {e}")
            return []

    def _analyze_by_location_sql(self, query) -> List[Dict]:
        """Análise por localização (SQL)."""
        try:
            # Subquery para encontrar o tema principal (mais complexo)
            # Vamos simplificar para o que o Pandas fazia: pegar o primeiro.
            # Nota: Uma análise de "main_theme" 100% em SQL é complexa.
            # Por performance, vamos manter a lógica do Pandas, mas SÓ para este campo.
            
            # Roda a agregação principal no SQL
            stmt = query.group_by(Mention.location).with_entities(
                Mention.location,
                func.count(Mention.id).label('total'),
                func.avg(Mention.quality_score).label('avg_quality'),
                func.avg(case((Mention.sentiment == 'POSITIVO', 1), (Mention.sentiment == 'NEGATIVO', 0), else_=None)).label('positive_rate_avg')
            ).order_by(func.count(Mention.id).desc()).limit(15)

            results = []
            for row in stmt.all():
                # Pega o tema principal (esta é a única parte que usa Pandas)
                theme_df = pd.DataFrame(query.filter(Mention.location == row.location).with_entities(Mention.theme).all(), columns=['theme'])
                main_theme = "Outros"
                if not theme_df.empty:
                    main_theme = theme_df['theme'].mode()[0] if not theme_df['theme'].mode().empty else 'Outros'

                results.append({
                    'location': row.location or 'Desconhecido',
                    'total': row.total,
                    'avg_quality': round(row.avg_quality or 0, 1),
                    'positive_rate': round((row.positive_rate_avg or 0) * 100, 1),
                    'main_theme': main_theme
                })
            return results
        except Exception as e:
            logger.error(f"Erro em _analyze_by_location_sql: {e}")
            return []

    def _analyze_by_sentiment_sql(self, query) -> Dict[str, int]:
        """Análise por sentimento (SQL)."""
        try:
            stmt = query.group_by(Mention.sentiment).with_entities(
                Mention.sentiment,
                func.count(Mention.id)
            )
            return {row[0] or 'NEUTRO': row[1] for row in stmt.all()}
        except Exception as e:
            logger.error(f"Erro em _analyze_by_sentiment_sql: {e}")
            return {}

    def _analyze_by_reliability_sql(self, query) -> Dict[str, Any]:
        """Análise por confiabilidade (SQL)."""
        try:
            stmt = query.group_by(Mention.reliability).with_entities(
                Mention.reliability,
                func.count(Mention.id).label('count'),
                func.avg(Mention.quality_score).label('avg_quality')
            )
            
            result = {'high': {'count': 0, 'avg_quality': 0}, 'medium': {'count': 0, 'avg_quality': 0}, 'low': {'count': 0, 'avg_quality': 0}}
            total = 0
            
            for row in stmt.all():
                level = row.reliability or 'medium'
                if level in result:
                    result[level]['count'] = row.count
                    result[level]['avg_quality'] = round(row.avg_quality or 0, 2)
                    total += row.count
            
            # Calcula porcentagens
            for level in result:
                result[level]['percentage'] = round((result[level]['count'] / total * 100), 1) if total > 0 else 0
                
            return result
        except Exception as e:
            logger.error(f"Erro em _analyze_by_reliability_sql: {e}")
            return {'high': {'count': 0, 'avg_quality': 0, 'percentage': 0}, 'medium': {'count': 0, 'avg_quality': 0, 'percentage': 0}, 'low': {'count': 0, 'avg_quality': 0, 'percentage': 0}}

    def generate_comparison_tables(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Gera tabelas de comparação (AGORA RODA EM SQL).
        'df' não é mais usado, 'filters' é passado para as sub-funções.
        """
        query = self._build_filtered_query(filters)
        
        tables = {}
        
        try: tables['source_comparison'] = self._analyze_by_source_sql(query)
        except Exception as e: logger.error(f"Erro source_comparison: {e}"); tables['source_comparison'] = []
        
        try: tables['theme_comparison'] = self._analyze_by_theme_sql(query)
        except Exception as e: logger.error(f"Erro theme_comparison: {e}"); tables['theme_comparison'] = []
        
        try: tables['location_comparison'] = self._analyze_by_location_sql(query)
        except Exception as e: logger.error(f"Erro location_comparison: {e}"); tables['location_comparison'] = []
        
        try: tables['temporal_analysis'] = self._create_temporal_analysis_sql(query)
        except Exception as e: logger.error(f"Erro temporal_analysis: {e}"); tables['temporal_analysis'] = []
        
        return convert_to_native_types(tables) # Converte tipos (como Decimal) para Python nativo

    def _create_temporal_analysis_sql(self, query) -> List[Dict]:
        """Análise temporal (SQL)."""
        try:
            # Agrupa por data completa (dia) para mostrar evolução diária
            stmt = query.group_by(func.strftime('%Y-%m-%d', Mention.timestamp_utc)).with_entities(
                func.strftime('%Y-%m-%d', Mention.timestamp_utc).label('date'),
                func.count(Mention.id).label('count'),
                func.avg(Mention.quality_score).label('avg_quality'),
                func.avg(case((Mention.sentiment == 'POSITIVO', 1), (Mention.sentiment == 'NEGATIVO', 0), else_=None)).label('positive_rate_avg')
            ).order_by(func.strftime('%Y-%m-%d', Mention.timestamp_utc))

            results = []
            for row in stmt.all():
                results.append({
                    'date': row.date,
                    'count': row.count,
                    'avg_quality': round(row.avg_quality or 0, 1),
                    'positive_rate': round((row.positive_rate_avg or 0) * 100, 1)
                })
            return results
        except Exception as e:
            logger.error(f"Erro temporal_analysis_sql: {e}")
            return []

    def export_analysis_report(self, analysis: Dict, df: pd.DataFrame = None) -> str:
        """Exporta relatório textual (agora não precisa mais do DataFrame)."""
        try:
            report = f"""
╔══════════════════════════════════════════════════════════════╗
║         RELATÓRIO DE ANÁLISE - TERMÔMETRO MA                ║
╚══════════════════════════════════════════════════════════════╝

📊 RESUMO GERAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total de Registros: {analysis.get('total_records', 0)}
Período: {analysis.get('date_range', {}).get('start', 'N/A')} até {analysis.get('date_range', {}).get('end', 'N/A')}

🎯 MÉTRICAS DE QUALIDADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Qualidade Média: {analysis.get('quality_metrics', {}).get('average_score', 0)}/100
Alta Qualidade (≥80): {analysis.get('quality_metrics', {}).get('high_quality_count', 0)} registros
Média Qualidade (50-79): {analysis.get('quality_metrics', {}).get('medium_quality_count', 0)} registros
Baixa Qualidade (<50): {analysis.get('quality_metrics', {}).get('low_quality_count', 0)} registros

📈 TOP 5 FONTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            for i, source in enumerate(analysis.get('by_source', [])[:5], 1):
                report += f"{i}. {source.get('source', 'N/A')}: {source.get('total', 0)} registros (Qualidade: {source.get('avg_quality', 0)})\n"
            
            report += f"""
🏷️  TOP 5 TEMAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            for i, theme in enumerate(analysis.get('by_theme', [])[:5], 1):
                report += f"{i}. {theme.get('theme', 'N/A')}: {theme.get('count', 0)} menções\n"
            
            report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
            
            return report
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return "Erro ao gerar relatório"