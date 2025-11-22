"""
TERMÔMETRO DO MARANHÃO - BIG DATA COLLECTION ENGINE
Otimizado para processar 3M+ dados (escala Big Data)

Volume esperado por fonte:
- Reclame Aqui: ~1.5M registros
- Google Maps: ~500K registros
- Procon/MP-MA: ~300K registros
- DataSUS: ~200K registros
- INEP: ~150K registros
- Transparência: ~200K registros
- Outros: ~150K registros
TOTAL: ~3.000.000+ registros
"""

import logging
import sys
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('massive_collection.log', 'w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

try:
    from backend.database import SessionLocal, engine
    from backend.models import Base, Mention
    from sqlalchemy import text
    
    # Coletores
    from backend.collectors.structured_data_collector import StructuredDataCollector
    from backend.collectors.google_maps_collector import GoogleMapsCollector
    from backend.collectors.public_opinion_collector import PublicOpinionCollector
    from backend.collectors.reclameaqui_collector import ReclameAquiAdvancedCollector
    from backend.collectors.procon_collector import ProconMPMACollector
    from backend.collectors.transparencia_collector import TransparencyCollector
    from backend.collectors.datasus_collector import DataSUSCollector
    from backend.collectors.inep_collector import INEPCollector
    
    # *** IMPORTA O ANALYZE PARA PRÉ-CÁLCULO ***
    from backend.collectors.data_analyzer import DataAnalyzer
    from backend.crud import create_mention # Usaremos o crud para criar objetos
    
except ImportError as e:
    logger.error(f"❌ Erro de importação: {e}")
    sys.exit(1)


def save_records_ULTRA_FAST(db, records, source_name, analyzer):
    """
    INSERÇÃO EM LOTE ULTRA-RÁPIDA
    50-100x mais rápido que inserção individual
    """
    if not records:
        logger.warning(f"⚠️ Nenhum registro de {source_name}")
        return 0
    
    logger.info(f"💾 Salvando {len(records):,} registros de {source_name}...")
    
    # OTIMIZAÇÃO: Não precisamos mais checar duplicatas aqui
    # O banco de dados vai ser recriado do zero
    
    # *** INÍCIO DA NOVA LÓGICA DE PRÉ-CÁLCULO ***
    logger.info(f"   🔍 Calculando scores de qualidade para {len(records):,} registros...")
    
    processed_records = []
    seen = set() # Deduplicação rápida em memória
    duplicates = 0

    for record in records:
        try:
            # 1. Deduplica
            record_text = record.get('text')
            if not record_text or record_text in seen:
                duplicates += 1
                continue
            seen.add(record_text)

            # 2. Normaliza timestamp
            if isinstance(record.get('timestamp_utc'), str):
                record['timestamp_utc'] = datetime.fromisoformat(record['timestamp_utc'].replace('Z', '+00:00'))
            elif not isinstance(record.get('timestamp_utc'), datetime):
                record['timestamp_utc'] = datetime.utcnow()
            
            # 3. Trunca texto
            if len(str(record_text)) > 1000:
                record['text'] = str(record_text)[:997] + '...'
            
            # 4. CALCULA QUALIDADE
            # Passamos o dict 'record' diretamente
            quality_data = analyzer.calculate_data_quality_score(record) 
            record.update(quality_data) # Adiciona 'quality_score', 'issues', 'reliability'
            
            processed_records.append(record)
            
        except Exception as e:
            logger.warning(f"   ⚠️ Erro ao processar registro: {e}")
            continue
    
    logger.info(f"   ✅ Scores calculados. {len(processed_records):,} únicos | {duplicates:,} duplicatas ignoradas")
    # *** FIM DA NOVA LÓGICA ***

    if not processed_records:
        logger.info(f"   ⚠️ Nenhum registro único para salvar.")
        return 0
    
    # BIG DATA: Inserção em LOTE otimizada para milhões de registros
    saved = 0
    batch_size = 10000  # BIG DATA: 10K por vez para máxima performance
    
    logger.info(f"   💾 Inserindo {len(processed_records):,} registros únicos em lotes...")
    
    for i in range(0, len(processed_records), batch_size):
        batch = processed_records[i:i + batch_size]
        
        try:
            # Cria objetos Mention
            # Usamos o crud.create_mention para garantir que todos os campos estão corretos
            mentions_objects = [create_mention(db, record) for record in batch]
            
            # Adiciona todos em 'add_all' (mais seguro que bulk_save_objects com objetos complexos)
            db.add_all(mentions_objects)
            db.commit()
            
            saved += len(batch)
            
            # Log de progresso
            if (i + batch_size) % 10000 == 0 or i + batch_size >= len(processed_records):
                logger.info(f"      ✅ {saved:,}/{len(processed_records):,} salvos...")
        
        except Exception as e:
            logger.error(f"   ❌ Erro no lote {i}-{i+batch_size}: {e}")
            db.rollback()
            continue
    
    logger.info(f"✅ {source_name}: {saved:,} salvos.")
    return saved


def run_massive_collection():
    """Executa coleta BIG DATA - 3M+ registros"""

    logger.info("=" * 80)
    logger.info("🚀 TERMÔMETRO DO MARANHÃO - BIG DATA COLLECTION (3M+ DADOS)")
    logger.info("=" * 80)
    logger.info("📊 Volume esperado: ~3.000.000 registros")
    logger.info("⏱️ Tempo estimado: 15-30 minutos")
    
    start_time = datetime.now()
    
    # Recria banco
    logger.info("\n🗄️ Recriando banco de dados...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # OTIMIZAÇÃO: Desabilita verificações do SQLite para velocidade máxima
    db = SessionLocal()
    try:
        db.execute(text("PRAGMA synchronous = OFF"))
        db.execute(text("PRAGMA journal_mode = MEMORY"))
        db.commit()
        logger.info("✅ Banco otimizado para velocidade máxima")
    except:
        pass
    
    # *** CRIA UMA INSTÂNCIA DO ANALYZER ***
    # Não precisa de 'db' para calcular scores
    analyzer = DataAnalyzer(db_session=None) 
    
    total_saved = 0
    
    try:
        # ========== 1. RECLAME AQUI (MAIOR VOLUME) ==========
        logger.info("\n" + "="*80)
        logger.info("📢 [1/8] RECLAME AQUI - 1.5M+ Reclamações (BIG DATA)")
        logger.info("="*80)
        try:
            reclame_aqui_collector = ReclameAquiAdvancedCollector()
            reclame_aqui_data = reclame_aqui_collector.collect_all_complaints()
            total_saved += save_records_ULTRA_FAST(db, reclame_aqui_data, "Reclame Aqui", analyzer)
        except Exception as e:
            logger.error(f"❌ Erro Reclame Aqui: {e}")
        
        # ========== 2. PROCON/MP-MA ==========
        logger.info("\n" + "="*80)
        logger.info("⚖️ [2/8] PROCON/MP-MA - 300K+ Reclamações (BIG DATA)")
        logger.info("="*80)
        try:
            procon_collector = ProconMPMACollector()
            procon_data = procon_collector.collect_all_data()
            total_saved += save_records_ULTRA_FAST(db, procon_data, "Procon/MP-MA", analyzer)
        except Exception as e:
            logger.error(f"❌ Erro Procon: {e}")
        
        # ========== 3. GOOGLE MAPS ==========
        logger.info("\n" + "="*80)
        logger.info("🗺️ [3/8] GOOGLE MAPS - 500K+ Avaliações (BIG DATA)")
        logger.info("="*80)
        try:
            gmaps_collector = GoogleMapsCollector()
            gmaps_data = gmaps_collector.collect_all_reviews()
            total_saved += save_records_ULTRA_FAST(db, gmaps_data, "Google Maps", analyzer)
        except Exception as e:
            logger.error(f"❌ Erro Google Maps: {e}")
        
        # ========== 4. DATASUS ==========
        logger.info("\n" + "="*80)
        logger.info("🏥 [4/8] DATASUS - 200K+ Indicadores de Saúde (BIG DATA)")
        logger.info("="*80)
        try:
            datasus_collector = DataSUSCollector()
            datasus_data = datasus_collector.collect_all_data()
            total_saved += save_records_ULTRA_FAST(db, datasus_data, "DATASUS", analyzer)
        except Exception as e:
            logger.error(f"❌ Erro DATASUS: {e}")
        
        # ========== 5. INEP ==========
        logger.info("\n" + "="*80)
        logger.info("📚 [5/8] INEP - 150K+ Indicadores de Educação (BIG DATA)")
        logger.info("="*80)
        try:
            inep_collector = INEPCollector()
            inep_data = inep_collector.collect_all_data()
            total_saved += save_records_ULTRA_FAST(db, inep_data, "INEP", analyzer)
        except Exception as e:
            logger.error(f"❌ Erro INEP: {e}")
        
        # ========== 6. PORTAL TRANSPARÊNCIA ==========
        logger.info("\n" + "="*80)
        logger.info("💰 [6/8] PORTAL DA TRANSPARÊNCIA - 200K+ Gastos Públicos (BIG DATA)")
        logger.info("="*80)
        try:
            transparency_collector = TransparencyCollector()
            transparency_data = transparency_collector.collect_all_data()
            total_saved += save_records_ULTRA_FAST(db, transparency_data, "Portal Transparência", analyzer)
        except Exception as e:
            logger.error(f"❌ Erro Transparência: {e}")
        
        # ========== 7. SEGURANÇA ==========
        logger.info("\n" + "="*80)
        logger.info("🚔 [7/8] FBSP - Dados de Segurança Pública")
        logger.info("="*80)
        try:
            security_collector = StructuredDataCollector()
            security_data = security_collector.get_security_data()
            total_saved += save_records_ULTRA_FAST(db, security_data, "FBSP Segurança", analyzer)
        except Exception as e:
            logger.error(f"❌ Erro Segurança: {e}")
        
        # ========== 8. OPINIÃO PÚBLICA ==========
        logger.info("\n" + "="*80)
        logger.info("💬 [8/8] OPINIÃO PÚBLICA - Notícias e Comentários")
        logger.info("="*80)
        try:
            # Tenta carregar config.json, se não achar, usa o scrapers_config.json
            config_file = "config.json"
            if not os.path.exists(config_file):
                config_file = "scrapers_config.json"
            
            if not os.path.exists(config_file):
                logger.error("❌ Arquivo config.json ou scrapers_config.json não encontrado")
            else:
                opinion_collector = PublicOpinionCollector(config_path=config_file)
                opinion_data = opinion_collector.collect_all_opinion_data()
                total_saved += save_records_ULTRA_FAST(db, opinion_data, "Opinião Pública", analyzer)
        except FileNotFoundError:
             logger.error("❌ Arquivo config.json ou scrapers_config.json não encontrado")
        except Exception as e:
            logger.error(f"❌ Erro Opinião Pública: {e}")
        
        # (Falta o passo 9/9 no seu script original, mas o log para em 8/8)
        # Se houver um coletor do IBGE, ele seria o 9/9
        
        # ========== RESUMO FINAL ==========
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("\n" + "="*80)
        logger.info("🎉 BIG DATA COLLECTION FINALIZADA!")
        logger.info("="*80)
        logger.info(f"✅ Total de registros salvos: {total_saved:,}")
        logger.info(f"⏱️ Tempo total: {duration:.2f}s ({duration/60:.2f} minutos)")
        if duration > 0:
            logger.info(f"📊 Velocidade: {total_saved/duration:.0f} registros/segundo")
        
        # Estatísticas
        from sqlalchemy import func
        
        logger.info("\n📈 ESTATÍSTICAS:")
        
        sentiment_stats = db.query(
            Mention.sentiment,
            func.count(Mention.id)
        ).group_by(Mention.sentiment).all()
        
        logger.info("\n   Por Sentimento:")
        for sentiment, count in sentiment_stats:
            percentage = (count / total_saved * 100) if total_saved > 0 else 0
            logger.info(f"      {sentiment or 'N/A'}: {count:,} ({percentage:.1f}%)")
        
        theme_stats = db.query(
            Mention.theme,
            func.count(Mention.id)
        ).group_by(Mention.theme).order_by(func.count(Mention.id).desc()).limit(10).all()
        
        logger.info("\n   Top 10 Temas:")
        for theme, count in theme_stats:
            percentage = (count / total_saved * 100) if total_saved > 0 else 0
            logger.info(f"      {theme or 'N/A'}: {count:,} ({percentage:.1f}%)")
        
        source_stats = db.query(
            Mention.source_platform,
            func.count(Mention.id)
        ).group_by(Mention.source_platform).order_by(func.count(Mention.id).desc()).all()
        
        logger.info("\n   Por Fonte:")
        for source, count in source_stats:
            percentage = (count / total_saved * 100) if total_saved > 0 else 0
            logger.info(f"      {source or 'N/A'}: {count:,} ({percentage:.1f}%)")
        
        logger.info("\n" + "="*80)
        logger.info("🚀 Sistema pronto! Execute:")
        logger.info("   python -m uvicorn backend.main:app --reload")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO: {e}", exc_info=True)
    
    finally:
        db.close()


if __name__ == "__main__":
    run_massive_collection()