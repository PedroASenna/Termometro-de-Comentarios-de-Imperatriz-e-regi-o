import logging
import json
from datetime import datetime

def setup_logging():
    """Configura o logging para arquivo e console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("collection.log", mode='w', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def normalize_and_save(data_records, platform, output_file):
    """
    Normaliza os dados para o formato padrão e salva em um arquivo .jsonl,
    preservando todos os campos existentes como 'sentimento'.
    """
    normalized_records = []
    
    for item in data_records:
        # Começa com todos os dados já processados (incluindo sentimento)
        record = item.copy()
        
        # Adiciona ou padroniza os campos principais
        record["source_platform"] = platform
        record["source_id"] = item.get("id", "")
        record["item_type"] = item.get("type", "comment")
        record["text"] = item.get("text", "")
        record["author"] = item.get("author", "N/A")
        record["timestamp_utc"] = item.get("timestamp", item.get("timestamp_utc", datetime.utcnow().isoformat()))
        record["location"] = "Imperatriz | Maranhão"
        record["metadata"] = item.get("metadata", {})
        
        normalized_records.append(record)

    # Salva no formato JSON Lines (.jsonl)
    with open(output_file, 'a', encoding='utf-8') as f:
        for record in normalized_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
    logging.info(f"Salvou e normalizou {len(normalized_records)} registros de '{platform}' em '{output_file}'")