"""
COLETOR DE DADOS (SIMULADO) - PROCON/MP-MA
Simula o registro de reclamações de consumidores no Maranhão.
"""

import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ProconMPMACollector:
    def __init__(self):
        self.cities_ma = [
            'São Luís', 'Imperatriz', 'Caxias', 'Timon', 'Codó',
            'Açailândia', 'Bacabal', 'Balsas', 'Paço do Lumiar',
            'Santa Inês', 'Pinheiro', 'Pedreiras', 'Chapadinha',
            'São José de Ribamar', 'Grajaú'
        ]
        
        self.complaint_templates = {
            'Produto com Defeito': [
                "Comprei {produto} na loja {empresa} em {cidade} e veio com defeito. Não querem trocar.",
                "Produto {produto} parou de funcionar com {dias} dias de uso. {empresa} nega garantia.",
                "{empresa} de {cidade} me vendeu {produto} com vício oculto. Exijo meu dinheiro de volta."
            ],
            'Cobrança Indevida': [
                "Banco {empresa} de {cidade} está me cobrando R$ {valor} por serviço não solicitado.",
                "Conta de telefone da {empresa} veio R$ {valor} mais cara. Cobrança indevida em {cidade}.",
                "{empresa} negativou meu nome por dívida de R$ {valor} que eu não reconheço."
            ],
            'Serviço Não Entregue': [
                "Contratei internet da {empresa} em {cidade} há {dias} dias e não instalaram.",
                "Compra online na {empresa} não foi entregue. Prazo expirou há {dias} dias.",
                "Paguei R$ {valor} pela instalação do {produto} e a {empresa} não apareceu."
            ]
        }
        
        self.products = ['Celular', 'TV', 'Geladeira', 'Sofá', 'Guarda-roupa', 'Notebook']
        self.companies = [
            'Lojas A', 'Banco B', 'Telefônica C', 'Magazine D', 'Varejista E',
            'Banco F', 'Lojas G', 'Eletro H', 'Varejo I', 'Telefônica J'
        ]
        
        logger.info("ℹ️ Coletor Procon/MP-MA (Simulado) inicializado.")

    def collect_all_data(self, num_complaints=1500):
        """Coleta todas as reclamações simuladas."""
        logger.info(f"⚖️ Iniciando coleta simulada de {num_complaints} reclamações do Procon/MP-MA...")
        records = []
        
        for _ in range(num_complaints):
            try:
                city = random.choice(self.cities_ma)
                complaint_type = random.choice(list(self.complaint_templates.keys()))
                template = random.choice(self.complaint_templates[complaint_type])
                
                text = template.format(
                    produto=random.choice(self.products),
                    empresa=random.choice(self.companies),
                    cidade=city,
                    dias=random.randint(10, 90),
                    valor=random.randint(50, 2000)
                )
                
                # Define o tema baseado no tipo de reclamação
                theme_map = {
                    'Produto com Defeito': 'Comércio',
                    'Cobrança Indevida': 'Comércio',
                    'Serviço Não Entregue': 'Infraestrutura'
                }
                
                records.append({
                    'source_platform': 'Procon/MP-MA',
                    'theme': theme_map.get(complaint_type, 'Comércio'),
                    'text': f"[{complaint_type}] {text}",
                    'sentiment': 'NEGATIVO', # Reclamações são inerentemente negativas
                    'location': city,
                    'timestamp_utc': datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                    'url': 'https://www.procon.ma.gov.br/reclamacoes-simuladas',
                    'indicator_name': 'Reclamação de Consumidor',
                    'indicator_value': 1,
                    'indicator_unit': 'reclamação',
                    'indicator_year': str(datetime.now().year)
                })
            except Exception as e:
                logger.error(f"Erro ao gerar registro do Procon: {e}")
                
        logger.info(f"✅ Coleta Procon/MP-MA finalizada: {len(records)} registros gerados.")
        return records