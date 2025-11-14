import logging
import requests
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)

def clean_html(raw_html):
    """Uma função simples para remover tags HTML e entidades como &nbsp;."""
    if not isinstance(raw_html, str):
        return ""
    clean_text = re.sub('<[^<]+?>', '', raw_html)  # Remove tags HTML
    clean_text = clean_text.replace('&nbsp;', ' ').strip() # Remove &nbsp; e espaços extras
    return clean_text

class GovDataCollector:
    def __init__(self, api_endpoints):
        self.api_endpoints = api_endpoints

    def fetch_all_data(self):
        logger.info("Iniciando coleta de dados governamentais.")
        all_records = []
        
        for name, url in self.api_endpoints.items():
            try:
                logger.info(f"Buscando dados de: {name} ({url})")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    logger.warning(f"Nenhum dado retornado de {name}.")
                    continue

                for record in data:
                    processed_record = None
                    record_id = None
                    
                    if name == 'vereadores' and isinstance(record, list) and len(record) >= 5:
                        processed_record = {
                            "nome": record[0], "cargo": record[1], "partido": record[2],
                            "email": record[3], "telefone": record[4]
                        }
                        record_id = record[0].replace(" ", "_").lower()
                    elif isinstance(record, dict):
                        processed_record = record
                        record_id = processed_record.get('id', processed_record.get('ID', ''))
                    else:
                        logger.warning(f"Registro ignorado em '{name}' devido a formato inesperado: {record}")
                        continue
                        
                    # --- LÓGICA DE EXTRAÇÃO DO TEXTO RELEVANTE ---
                    # Tenta encontrar o "Objeto" do contrato, que é a parte mais importante.
                    relevant_text = processed_record.get('Objeto', processed_record.get('objeto', str(processed_record)))
                    clean_text = clean_html(relevant_text)
                    # -----------------------------------------------

                    all_records.append({
                        "id": f"gov_{name}_{record_id}",
                        "type": "government_record",
                        "text": clean_text, # << AQUI ESTÁ A MUDANÇA PRINCIPAL
                        "author": "Câmara de Imperatriz",
                        "timestamp": processed_record.get('data', datetime.utcnow().isoformat()),
                        "metadata": processed_record
                    })
                logger.info(f"Coletou {len(data)} registros de {name}.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro de rede ao buscar dados de {url}: {e}")
            except json.JSONDecodeError:
                logger.error(f"Erro ao decodificar JSON de {url}")
            except Exception as e:
                logger.error(f"Erro inesperado ao processar {url}: {e}", exc_info=True)

        logger.info(f"Coleta de dados governamentais finalizada. Total de {len(all_records)} registros.")
        return all_records