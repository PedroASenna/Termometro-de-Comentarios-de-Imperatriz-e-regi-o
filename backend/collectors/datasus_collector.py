"""
COLETOR DE DADOS (SIMULADO) - DATASUS
Simula o registro de indicadores de saúde pública (leitos, dengue, etc.).
"""

import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataSUSCollector:
    def __init__(self):
        self.cities_ma = [
            'São Luís', 'Imperatriz', 'Caxias', 'Timon', 'Codó',
            'Açailândia', 'Bacabal', 'Balsas', 'Paço do Lumiar',
            'Santa Inês', 'Pinheiro', 'Pedreiras', 'Chapadinha',
            'São José de Ribamar', 'Grajaú'
        ]
        
        self.indicators = {
            'Leitos_UTI': {
                'name': 'Leitos de UTI (Ocupação)',
                'unit': '%',
                'min_val': 40,
                'max_val': 95,
                'sentiment': lambda v: 'NEGATIVO' if v > 80 else ('NEUTRO' if v > 60 else 'POSITIVO')
            },
            'Casos_Dengue': {
                'name': 'Casos Confirmados de Dengue (Mês)',
                'unit': 'casos',
                'min_val': 5,
                'max_val': 300,
                'sentiment': lambda v: 'NEGATIVO' if v > 100 else 'NEUTRO'
            },
            'Atendimentos_Hospitalares': {
                'name': 'Atendimentos Hospitalares (Emergência)',
                'unit': 'atendimentos/dia',
                'min_val': 50,
                'max_val': 500,
                'sentiment': lambda v: 'NEUTRO'
            }
        }
        
        logger.info("ℹ️ Coletor DataSUS (Simulado) inicializado.")

    def collect_all_data(self):
        """Coleta todos os indicadores simulados do DataSUS."""
        logger.info("🏥 Iniciando coleta simulada de indicadores do DataSUS...")
        records = []
        year = str(datetime.now().year - 1) # Dados consolidados do ano anterior
        
        for city in self.cities_ma:
            for indicator_id, config in self.indicators.items():
                try:
                    value = random.randint(config['min_val'], config['max_val'])
                    
                    # Ajusta valores para cidades principais
                    if city in ['São Luís', 'Imperatriz']:
                        value = int(value * random.uniform(1.5, 3.0))
                    
                    sentiment = config['sentiment'](value)
                    
                    records.append({
                        'source_platform': 'DATASUS',
                        'theme': 'Saúde',
                        'text': f"{config['name']} em {city}: {value} {config['unit']} (Ano: {year})",
                        'sentiment': sentiment,
                        'location': city,
                        'timestamp_utc': datetime.utcnow() - timedelta(days=random.randint(30, 90)),
                        'url': 'https://datasus.saude.gov.br/informacoes-de-saude-tabnet-simulado/',
                        'indicator_id': indicator_id,
                        'indicator_name': config['name'],
                        'indicator_value': float(value),
                        'indicator_unit': config['unit'],
                        'indicator_year': year
                    })
                except Exception as e:
                    logger.error(f"Erro ao gerar registro do DataSUS: {e}")
                    
        logger.info(f"✅ Coleta DataSUS finalizada: {len(records)} registros gerados.")
        return records