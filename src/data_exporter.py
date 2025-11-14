"""
Módulo para exportar os dados processados para formatos de BI como CSV.
"""
import pandas as pd
import os
from pathlib import Path
from src.config import DATA_PATHS
import logging

logger = logging.getLogger(__name__)

class DataExporter:
    def __init__(self):
        self.results_path = DATA_PATHS['results']
        # Garante que o diretório de resultados exista
        Path(self.results_path).mkdir(parents=True, exist_ok=True)
    
    def export_for_bi(self, df):
        """
        Salva o DataFrame final em um arquivo CSV com nome fixo para Power BI.
        
        Args:
            df (pandas.DataFrame): O DataFrame final com todos os dados e análises.
            
        Returns:
            str: O caminho do arquivo salvo.
        """
        if df.empty:
            logger.error("DataFrame vazio. Nenhum dado para exportar.")
            return None
        
        # Define um nome de arquivo fixo para facilitar a conexão persistente com o Power BI
        output_filename = "power_bi_data.csv"
        filepath = os.path.join(self.results_path, output_filename)
        
        try:
            # Salva o arquivo em formato CSV
            # encoding='utf-8-sig' garante compatibilidade com acentos no Power BI/Excel
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"Dados exportados com sucesso para: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Falha ao exportar dados para CSV: {str(e)}")
            return None