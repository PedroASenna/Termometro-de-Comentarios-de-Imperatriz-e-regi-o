"""
COLETOR DE DADOS (SIMULADO) - PORTAL DA TRANSPARÊNCIA
Simula o registro de gastos públicos e investimentos.
"""

import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TransparencyCollector:
    def __init__(self):
        self.cities_ma = [
            'São Luís', 'Imperatriz', 'Caxias', 'Timon', 'Codó',
            'Açailândia', 'Bacabal', 'Balsas', 'Paço do Lumiar',
            'Santa Inês', 'Pinheiro', 'Pedreiras', 'Chapadinha'
        ]
        
        self.investment_areas = {
            'Saúde': {
                'name': 'Investimento em Saúde (Mensal)',
                'unit': 'R$',
                'min_val': 500000,
                'max_val': 10000000,
                'sentiment': 'NEUTRO'
            },
            'Educação': {
                'name': 'Investimento em Educação (Mensal)',
                'unit': 'R$',
                'min_val': 700000,
                'max_val': 12000000,
                'sentiment': 'NEUTRO'
            },
            'Infraestrutura': {
                'name': 'Gastos com Obras e Infraestrutura (Mensal)',
                'unit': 'R$',
                'min_val': 200000,
                'max_val': 5000000,
                'sentiment': 'NEUTRO'
            }
        }
        
        logger.info("ℹ️ Coletor Portal da Transparência (Simulado) inicializado.")

    def collect_all_data(self):
        """Coleta todos os indicadores simulados de transparência."""
        logger.info("💰 Iniciando coleta simulada de dados do Portal da Transparência...")
        records = []
        year = str(datetime.now().year)
        
        for city in self.cities_ma:
            for theme, config in self.investment_areas.items():
                try:
                    value = random.randint(config['min_val'], config['max_val'])
                    
                    # Ajusta valores para cidades principais
                    if city in ['São Luís', 'Imperatriz']:
                        value = int(value * random.uniform(2.0, 5.0))
                    
                    records.append({
                        'source_platform': 'Portal da Transparência',
                        'theme': theme,
                        'text': f"{config['name']} em {city}: R$ {value:,.2f} (Ref: {year})",
                        'sentiment': config['sentiment'],
                        'location': city,
                        'timestamp_utc': datetime.utcnow() - timedelta(days=random.randint(15, 60)),
                        'url': 'https://www.portaltransparencia.gov.br/simulado',
                        'indicator_id': f"gastos_{theme.lower()}",
                        'indicator_name': config['name'],
                        'indicator_value': float(value),
                        'indicator_unit': config['unit'],
                        'indicator_year': year
                    })
                except Exception as e:
                    logger.error(f"Erro ao gerar registro de Transparência: {e}")
                    
        logger.info(f"✅ Coleta Portal da Transparência finalizada: {len(records)} registros gerados.")
        return records