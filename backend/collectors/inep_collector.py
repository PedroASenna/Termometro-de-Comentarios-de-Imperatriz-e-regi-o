"""
COLETOR DE DADOS (SIMULADO) - INEP
Simula o registro de indicadores de educação (IDEB, Abandono Escolar).
"""

import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class INEPCollector:
    def __init__(self):
        self.cities_ma = [
            'São Luís', 'Imperatriz', 'Caxias', 'Timon', 'Codó',
            'Açailândia', 'Bacabal', 'Balsas', 'Paço do Lumiar',
            'Santa Inês', 'Pinheiro', 'Pedreiras', 'Chapadinha',
            'São José de Ribamar', 'Grajaú'
        ]
        
        self.indicators = {
            'IDEB_Anos_Iniciais': {
                'name': 'IDEB - Anos Iniciais (Rede Pública)',
                'unit': 'nota',
                'min_val': 3.5,
                'max_val': 6.0,
                'sentiment': lambda v: 'POSITIVO' if v > 5.0 else ('NEUTRO' if v > 4.0 else 'NEGATIVO')
            },
            'IDEB_Anos_Finais': {
                'name': 'IDEB - Anos Finais (Rede Pública)',
                'unit': 'nota',
                'min_val': 3.0,
                'max_val': 5.5,
                'sentiment': lambda v: 'POSITIVO' if v > 4.5 else ('NEUTRO' if v > 3.5 else 'NEGATIVO')
            },
            'Taxa_Abandono_Medio': {
                'name': 'Taxa de Abandono (Ensino Médio)',
                'unit': '%',
                'min_val': 2.0,
                'max_val': 15.0,
                'sentiment': lambda v: 'NEGATIVO' if v > 10 else ('NEUTRO' if v > 5 else 'POSITIVO')
            }
        }
        
        logger.info("ℹ️ Coletor INEP (Simulado) inicializado.")

    def collect_all_data(self):
        """Coleta todos os indicadores simulados do INEP."""
        logger.info("📚 Iniciando coleta simulada de indicadores do INEP...")
        records = []
        year = str(datetime.now().year - 2) # Dados do IDEB são bienais
        
        for city in self.cities_ma:
            for indicator_id, config in self.indicators.items():
                try:
                    value = round(random.uniform(config['min_val'], config['max_val']), 1)
                    sentiment = config['sentiment'](value)
                    
                    records.append({
                        'source_platform': 'INEP',
                        'theme': 'Educação',
                        'text': f"{config['name']} em {city}: {value} {config['unit']} (Ano: {year})",
                        'sentiment': sentiment,
                        'location': city,
                        'timestamp_utc': datetime.utcnow() - timedelta(days=random.randint(60, 120)),
                        'url': 'https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb-simulado',
                        'indicator_id': indicator_id,
                        'indicator_name': config['name'],
                        'indicator_value': float(value),
                        'indicator_unit': config['unit'],
                        'indicator_year': year
                    })
                except Exception as e:
                    logger.error(f"Erro ao gerar registro do INEP: {e}")
                    
        logger.info(f"✅ Coleta INEP finalizada: {len(records)} registros gerados.")
        return records