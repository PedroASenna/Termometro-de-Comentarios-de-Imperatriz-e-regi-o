"""
Módulo para limpeza e pré-processamento de dados textuais.
"""
import re
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataCleaner:
    def _clean_text(self, text):
        if not isinstance(text, str):
            return ""
        text = re.sub(r'http\S+', '', text)  # Remove URLs
        text = re.sub(r'@[A-Za-z0-9_]+', '', text)  # Remove menções
        text = re.sub(r'#', '', text)  # Remove o símbolo de hashtag
        text = re.sub(r'[^\w\sáàâãéèêíïóôõöúçñ]', '', text)  # Remove caracteres especiais
        text = re.sub(r'\s+', ' ', text).strip()  # Remove espaços extras
        return text.lower()

    def process(self, raw_data_list):
        if not raw_data_list:
            logger.warning("Nenhuma lista de dados brutos para processar.")
            return pd.DataFrame()
        
        df = pd.DataFrame(raw_data_list)
        df.drop_duplicates(subset=['id'], inplace=True)

        df['texto_limpo'] = df['texto_original'].apply(self._clean_text)
        df = df[df['texto_limpo'].str.len() > 10]
        
        df['data_criacao'] = pd.to_datetime(df['data_criacao'])
        
        logger.info(f"Limpeza concluída. {len(df)} registros válidos restantes.")
        return df