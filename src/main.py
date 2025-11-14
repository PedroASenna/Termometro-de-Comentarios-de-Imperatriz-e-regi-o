import logging
import configparser
import pandas as pd
from src.utils import setup_logging, normalize_and_save
from src.collectors.news_scraper import NewsScraper
from src.collectors.structured_data_collector import StructuredDataCollector
from src.data_cleaner import DataCleaner
from src.sentiment_analyzer import SentimentAnalyzer

THEME_KEYWORDS = {
    'Segurança': ['polícia', 'crime', 'assalto', 'roubo', 'homicídio', 'violência', 'ssp-ma', 'segurança', 'preso', 'operação policial', 'delegacia', 'viatura'],
    'Infraestrutura': ['rua', 'buraco', 'asfalto', 'ponte', 'obra', 'saneamento', 'caema', 'energia', 'cemar', 'trânsito', 'semáforo', 'iluminação'],
    'Comércio': ['preço', 'comércio', 'supermercado', 'loja', 'consumidor', 'procon', 'economia', 'inflação', 'vendas', 'juros', 'cesta básica']
}
THEME_PRIORITY = ['Segurança', 'Infraestrutura', 'Comércio']

def categorize_text(text):
    text_lower = text.lower()
    for theme in THEME_PRIORITY:
        if any(keyword in text_lower for keyword in THEME_KEYWORDS[theme]):
            return theme
    return 'Outros'

def process_and_save(data, platform, filename, cleaner, analyzer):
    if not data: return
    df = pd.DataFrame(data)
    df['texto_limpo'] = df['text'].apply(cleaner._clean_text)
    df = df[df['texto_limpo'].str.len() > 20]
    if df.empty: return

    df['theme'] = df['texto_limpo'].apply(categorize_text)
    analyzed_df = analyzer.analyze(df)
    
    records_to_save = analyzed_df.to_dict('records')
    normalize_and_save(records_to_save, platform, filename)

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(">>> INICIANDO O TERMÔMETRO DO MARANHÃO (V2) <<<")
    
    cleaner = DataCleaner()
    analyzer = SentimentAnalyzer()

    # --- 1. Coleta de Dados Estruturados (Estatísticas) ---
    try:
        structured_collector = StructuredDataCollector()
        security_data = structured_collector.get_security_data()
        if security_data:
            # Dados estatísticos não precisam de análise de sentimento
            normalize_and_save(security_data, "FBSP", "structured_security_data.jsonl")
    except Exception as e:
        logger.error(f"Falha crítica no coletor de dados estruturados: {e}", exc_info=True)

    # --- 2. Coleta de Dados Não Estruturados (Notícias) ---
    try:
        news_scraper = NewsScraper(config_path='scrapers_config.json')
        news_data = news_scraper.scrape_all_sites()
        process_and_save(news_data, "news_portal", "news_data.jsonl", cleaner, analyzer)
    except Exception as e:
        logger.error(f"Falha crítica no scraper de notícias: {e}", exc_info=True)
    
    logger.info(">>> PIPELINE DE COLETA E ANÁLISE FINALIZADO <<<")

if __name__ == "__main__":
    main()