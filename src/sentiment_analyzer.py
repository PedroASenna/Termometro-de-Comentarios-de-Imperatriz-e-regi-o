"""
Módulo para análise de sentimentos usando um modelo pré-treinado (Transformers).
"""
from transformers import pipeline
import pandas as pd
import logging
from src.config import MODEL_SETTINGS

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        try:
            logger.info(f"Carregando modelo de análise de sentimentos: {MODEL_SETTINGS['model_name']}")
            self.model = pipeline(
                'sentiment-analysis',
                model=MODEL_SETTINGS['model_name']
            )
            logger.info("Modelo carregado com sucesso!")
        except Exception as e:
            logger.error(f"Falha ao carregar o modelo de sentimentos: {e}", exc_info=True)
            self.model = None

    def analyze(self, df):
        if self.model is None or df.empty:
            logger.error("Análise não pode ser realizada. Modelo não carregado ou DataFrame vazio.")
            df['sentimento'] = 'N/A'
            df['confianca'] = 0.0
            return df

        texts = df['texto_limpo'].tolist()
        try:
            results = self.model(texts, truncation=True, max_length=MODEL_SETTINGS['max_length'])
            df['sentimento'] = [result['label'] for result in results]
            df['confianca'] = [result['score'] for result in results]
            
            # Padronizando labels para POSITIVO/NEGATIVO/NEUTRO
            df['sentimento'] = df['sentimento'].replace({'LABEL_1': 'POSITIVO', 'LABEL_0': 'NEGATIVO', 'LABEL_2': 'NEUTRO'})

            logger.info("Análise de sentimentos concluída.")
        except Exception as e:
            logger.error(f"Erro durante a análise de sentimentos: {e}", exc_info=True)
            df['sentimento'] = 'ERRO'
            df['confianca'] = 0.0
        
        return df