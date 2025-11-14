import logging
import pandas as pd
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

class StructuredDataCollector:
    def __init__(self):
        self.fbsp_url = "https://forumseguranca.org.br/wp-content/uploads/2023/07/anuario-2023.xlsx"

    def get_security_data(self):
        logger.info(f"Baixando dados de segurança de: {self.fbsp_url}")
        try:
            response = requests.get(self.fbsp_url)
            response.raise_for_status()
            
            # --- LÓGICA ROBUSTA PARA ENCONTRAR A PLANILHA CORRETA ---
            xls = pd.ExcelFile(BytesIO(response.content))
            target_sheet_name = None
            for sheet_name in xls.sheet_names:
                # Procura por uma planilha que contenha "MVI" e "Municípios" no nome
                if "MVI" in sheet_name and "Municípios" in sheet_name:
                    target_sheet_name = sheet_name
                    break
            
            if not target_sheet_name:
                logger.error("ERRO CRÍTICO: Nenhuma planilha com dados de MVI por município foi encontrada no arquivo Excel.")
                return []

            logger.info(f"Planilha de dados encontrada: '{target_sheet_name}'")
            df = pd.read_excel(xls, sheet_name=target_sheet_name, skiprows=1)
            
            df_ma = df[df['UF'] == 'MA'].copy()
            
            if df_ma.empty:
                logger.warning("Nenhum dado para o Maranhão encontrado no Anuário.")
                return []

            records = []
            for _, row in df_ma.iterrows():
                crime_rate = row.get('MVI (Polícia Civil)', 0) 
                city = row['Município']
                
                records.append({
                    "id": f"fbsp_mvi_{city.replace(' ', '_')}",
                    "type": "statistic_record", "theme": "Segurança",
                    "text": f"Mortes Violentas Intencionais em {city}: {crime_rate}",
                    "author": "Fórum Brasileiro de Segurança Pública",
                    "timestamp": "2023-07-20T00:00:00Z", "location": city,
                    "metadata": { "indicator": "Mortes Violentas Intencionais", "value": crime_rate, "year": 2022 }
                })
            
            logger.info(f"Processou {len(records)} registros de segurança para o Maranhão.")
            return records

        except Exception as e:
            logger.error(f"Falha ao baixar ou processar dados do Fórum de Segurança: {e}", exc_info=True)
            return []