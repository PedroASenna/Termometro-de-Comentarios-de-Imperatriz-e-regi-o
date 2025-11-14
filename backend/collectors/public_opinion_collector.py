"""
PUBLIC OPINION COLLECTOR - VERSÃO CORRIGIDA
Remove campos inválidos do modelo Mention
"""

import logging
import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin, quote_plus
import time
import random

logger = logging.getLogger(__name__)

class PublicOpinionCollector:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # URLs de fóruns e sites de opinião específicos do Maranhão
        self.opinion_sources = {
            'forums_locais': [
                'https://www.skyscrapercity.com/forums/comunidade-maranhense.2047/',
                'https://www.facebook.com/groups/saoluisma/',
                'https://www.facebook.com/groups/imperatrizma/'
            ],
            'google_reviews': {
                'categories': ['hospital', 'escola', 'transporte publico', 'prefeitura'],
                'location': 'Maranhão, Brasil'
            }
        }
        
        # Padrões de reclamação e elogio mais específicos
        self.opinion_patterns = {
            'reclamations': [
                r'(?:péssimo|terrível|horrível|vergonha|abandono|descaso)\s+(?:atendimento|serviço|situação)',
                r'(?:não funciona|está quebrado|fora de ordem|em péssimo estado)',
                r'(?:demora|espera|fila)\s+(?:excessiva|absurda|ridícula)',
                r'(?:falta de|sem|não tem)\s+(?:segurança|iluminação|asfalto|sinalização)',
                r'(?:muito caro|preço abusivo|exploração)'
            ],
            'compliments': [
                r'(?:excelente|ótimo|muito bom|perfeito)\s+(?:atendimento|serviço)',
                r'(?:melhorou muito|grande melhoria|progresso visível)',
                r'(?:parabéns|reconhecimento|elogio)\s+(?:pela|ao|à)',
                r'(?:rápido|eficiente|pontual)\s+(?:atendimento|serviço)',
                r'(?:satisfeito|contente|feliz)\s+com\s+(?:o|a)',
                r'(?:recomendo|indico|aprovado)'
            ],
            'neutral_indicators': [
                r'(?:regular|normal|mediano|na média)',
                r'(?:poderia melhorar|tem potencial|precisa de ajustes)',
                r'(?:não é ruim|não é excelente|mediano)'
            ]
        }
        
        # Cidades do Maranhão por importância
        self.ma_cities_priority = [
            'São Luís', 'Imperatriz', 'Caxias', 'Timon', 'Codó', 'Paço do Lumiar',
            'Açailândia', 'Bacabal', 'Balsas', 'Santa Inês', 'Pinheiro', 'Pedreiras',
            'Chapadinha', 'São José de Ribamar', 'Grajaú', 'Itapecuru Mirim',
            'Presidente Dutra', 'Viana', 'São Mateus', 'Rosário'
        ]

    def _get_soup(self, url, retries=2):
        """Requisição com tratamento de erro."""
        for attempt in range(retries):
            try:
                time.sleep(random.uniform(1, 2))
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                if attempt == retries - 1:
                    logger.warning(f"Falha ao acessar {url}: {e}")
                    return None
                time.sleep(2)
        return None

    def _analyze_opinion_sentiment(self, text):
        """Análise de sentimento específica para opiniões públicas."""
        text_lower = text.lower()
        
        complaint_score = 0
        compliment_score = 0
        
        # Verifica padrões de reclamação
        for pattern in self.opinion_patterns['reclamations']:
            if re.search(pattern, text_lower):
                complaint_score += 2
        
        # Verifica padrões de elogio
        for pattern in self.opinion_patterns['compliments']:
            if re.search(pattern, text_lower):
                compliment_score += 2
        
        # Palavras-chave específicas
        negative_keywords = [
            'péssimo', 'terrível', 'horrível', 'vergonha', 'lamentável', 'revoltante',
            'inadmissível', 'absurdo', 'ridículo', 'inaceitável', 'abandono', 'descaso',
            'negligência', 'demora excessiva', 'fila quilométrica', 'não funciona',
            'está quebrado', 'péssimo estado', 'muito caro', 'abusivo'
        ]
        
        positive_keywords = [
            'excelente', 'ótimo', 'muito bom', 'perfeito', 'maravilhoso', 'fantástico',
            'melhorou muito', 'grande melhoria', 'parabéns', 'reconheço', 'elogio',
            'satisfeito', 'recomendo', 'aprovado', 'eficiente', 'rápido', 'pontual'
        ]
        
        for keyword in negative_keywords:
            if keyword in text_lower:
                complaint_score += 1
        
        for keyword in positive_keywords:
            if keyword in text_lower:
                compliment_score += 1
        
        if compliment_score > complaint_score:
            return 'POSITIVO'
        elif complaint_score > compliment_score:
            return 'NEGATIVO'
        else:
            return 'NEUTRO'

    def _categorize_complaint(self, text):
        """Categoriza reclamação por tema."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['agua', 'esgoto', 'caema', 'saneamento']):
            return 'Infraestrutura'
        elif any(word in text_lower for word in ['energia', 'luz', 'cemar', 'eletrica']):
            return 'Infraestrutura'
        elif any(word in text_lower for word in ['hospital', 'saude', 'medico', 'sus']):
            return 'Saúde'
        elif any(word in text_lower for word in ['prefeitura', 'municipal', 'servico publico']):
            return 'Administração Pública'
        elif any(word in text_lower for word in ['transporte', 'onibus', 'rodoviario']):
            return 'Transporte'
        elif any(word in text_lower for word in ['shopping', 'loja', 'comercio']):
            return 'Comércio'
        else:
            return 'Outros'

    def _extract_city_from_company(self, company):
        """Extrai cidade baseada na empresa."""
        if 'São Luís' in company or 'CAEMA' in company or 'HU-UFMA' in company:
            return 'São Luís'
        elif 'Imperatriz' in company:
            return 'Imperatriz'
        elif 'CEMAR' in company or 'DETRAN' in company:
            return random.choice(self.ma_cities_priority[:5])
        else:
            return 'São Luís'

    def collect_google_reviews_simulation(self):
        """Simula coleta de avaliações do Google para estabelecimentos do Maranhão."""
        logger.info("Simulando coleta de avaliações do Google...")
        records = []
        
        establishments = [
            {'name': 'Hospital Municipal de São Luís', 'city': 'São Luís', 'category': 'Saúde'},
            {'name': 'Escola Estadual São Luís', 'city': 'São Luís', 'category': 'Educação'},
            {'name': 'Terminal de Integração da Praia Grande', 'city': 'São Luís', 'category': 'Transporte'},
            {'name': 'Hospital Municipal de Imperatriz', 'city': 'Imperatriz', 'category': 'Saúde'},
            {'name': 'Prefeitura Municipal de Caxias', 'city': 'Caxias', 'category': 'Administração Pública'},
            {'name': 'Terminal Rodoviário de Codó', 'city': 'Codó', 'category': 'Transporte'},
            {'name': 'Hospital Regional de Bacabal', 'city': 'Bacabal', 'category': 'Saúde'}
        ]
        
        review_templates = {
            'positive': [
                "Atendimento muito bom, funcionários educados",
                "Melhorou bastante nos últimos meses",
                "Serviço eficiente e rápido",
                "Recomendo, tive uma boa experiência",
                "Funcionários prestativos e lugar organizado"
            ],
            'negative': [
                "Atendimento péssimo, muita demora",
                "Falta de organização e funcionários mal educados",
                "Serviço de muito baixa qualidade",
                "Não recomendo, experiência terrível",
                "Lugar sujo e mal conservado"
            ],
            'neutral': [
                "Serviço regular, pode melhorar",
                "Atendimento na média, nada excepcional",
                "Tem potencial mas precisa de melhorias",
                "Não é ruim mas também não é excelente"
            ]
        }
        
        for establishment in establishments:
            num_reviews = random.randint(8, 20)
            
            for _ in range(num_reviews):
                sentiment_type = random.choices(
                    ['negative', 'positive', 'neutral'], 
                    weights=[0.5, 0.3, 0.2]  # Mais reviews negativas (realista)
                )[0]
                
                review_text = random.choice(review_templates[sentiment_type])
                rating = random.randint(1, 5)
                
                # ✅ CORREÇÃO: Rating e establishment no texto
                full_review = f"{review_text} - {establishment['name']} [Nota: {rating}/5]"
                
                # ***** CORREÇÃO AQUI *****
                # Converte 'positive'/'negative'/'neutral' para 'POSITIVO'/'NEGATIVO'/'NEUTRO'
                if sentiment_type == 'positive':
                    sentiment_portugues = 'POSITIVO'
                elif sentiment_type == 'negative':
                    sentiment_portugues = 'NEGATIVO'
                else:
                    sentiment_portugues = 'NEUTRO'

                records.append({
                    "source_platform": "google_reviews",
                    "theme": establishment['category'],
                    "text": full_review,  # ✅ Rating agora no texto
                    "sentiment": sentiment_portugues, # ✅ Sentimento padronizado
                    "location": establishment['city'],
                    "timestamp_utc": datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                    "url": f"https://www.google.com/maps/place/{establishment['name'].replace(' ', '+')}"
                    # ✅ REMOVIDO: 'rating' e 'establishment' (campos inválidos)
                })
        
        logger.info(f"Simulados {len(records)} reviews do Google")
        return records

    def collect_social_media_mentions(self):
        """Simula coleta de menções em redes sociais sobre cidades do Maranhão."""
        logger.info("Simulando coleta de menções em redes sociais...")
        records = []
        
        social_mentions = [
            # Menções negativas realistas
            "Trânsito de São Luís está um caos, não aguento mais!",
            "Buracos na Avenida João Pessoa em Imperatriz, um absurdo",
            "Hospital da Criança lotado, que situação triste",
            "Falta energia em Codó de novo, CEMAR pelo amor de Deus!",
            "Transporte público de São Luís é uma vergonha nacional",
            "Insegurança em Caxias tá demais, polícia cadê?",
            "Ruas alagadas em Bacabal toda vez que chove",
            
            # Menções positivas realistas
            "Nova escola inaugurada em Timon, que alegria!",
            "Pavimentação da rua principal em Pedreiras ficou ótima",
            "Atendimento no posto de saúde melhorou muito aqui em Chapadinha",
            "Praça renovada em Pinheiro ficou linda, parabéns!",
            "Nova ponte em Açailândia vai facilitar muito o trânsito",
            
            # Menções neutras
            "Obras na BR-135 devem terminar em 6 meses",
            "Prefeitura de Balsas anuncia novo projeto para 2024",
            "Reunião sobre saneamento em Santa Inês na próxima semana"
        ]
        
        platforms = ['facebook', 'instagram', 'twitter', 'whatsapp_groups']
        
        for mention in social_mentions:
            platform = random.choice(platforms)
            city = self._extract_city_from_mention(mention)
            engagement = random.randint(5, 200)
            
            # ✅ CORREÇÃO: Engagement e platform_type no texto
            full_mention = f"{mention} [Engajamento: {engagement} | Plataforma: {platform}]"
            
            records.append({
                "source_platform": f"social_{platform}",
                "theme": self._categorize_social_mention(mention),
                "text": full_mention,  # ✅ Metadados agora no texto
                "sentiment": self._analyze_opinion_sentiment(mention), # ✅ Já retorna em Português
                "location": city,
                "timestamp_utc": datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                "url": f"https://{platform.split('_')[0]}.com/post_simulado"
                # ✅ REMOVIDO: 'engagement' e 'platform_type' (campos inválidos)
            })
        
        # Adiciona mais menções baseadas em padrões sazonais
        seasonal_mentions = self._generate_seasonal_mentions()
        records.extend(seasonal_mentions)
        
        logger.info(f"Simuladas {len(records)} menções de redes sociais")
        return records

    def _extract_city_from_mention(self, mention):
        """Extrai cidade da menção."""
        mention_lower = mention.lower()
        
        for city in self.ma_cities_priority:
            if city.lower() in mention_lower:
                return city
        
        return 'Maranhão'

    def _categorize_social_mention(self, mention):
        """Categoriza menção de rede social."""
        mention_lower = mention.lower()
        
        if any(word in mention_lower for word in ['transito', 'onibus', 'rua', 'avenida', 'br-', 'ponte']):
            return 'Transporte'
        elif any(word in mention_lower for word in ['hospital', 'posto', 'saude', 'medico']):
            return 'Saúde'
        elif any(word in mention_lower for word in ['escola', 'educacao', 'professor']):
            return 'Educação'
        elif any(word in mention_lower for word in ['seguranca', 'policia', 'crime', 'violencia']):
            return 'Segurança'
        elif any(word in mention_lower for word in ['energia', 'luz', 'agua', 'esgoto']):
            return 'Infraestrutura'
        elif any(word in mention_lower for word in ['prefeitura', 'prefeito', 'projeto', 'obra']):
            return 'Administração Pública'
        else:
            return 'Outros'

    def _generate_seasonal_mentions(self):
        """Gera menções baseadas em padrões sazonais."""
        current_month = datetime.now().month
        seasonal_records = []
        
        # Menções típicas da época de chuvas (dezembro a maio)
        if current_month in [12, 1, 2, 3, 4, 5]:
            rain_mentions = [
                "Alagamento na baixada maranhense de novo",
                "Ruas de São Luís viraram rios, que situação!",
                "Drenagem de Imperatriz não aguenta a chuva",
                "Temporal em Caxias deixou várias famílias desabrigadas"
            ]
            
            for mention in rain_mentions:
                seasonal_records.append({
                    "source_platform": "social_seasonal",
                    "theme": "Infraestrutura",
                    "text": f"{mention} [Tipo: Período Chuvoso]",
                    "sentiment": "NEGATIVO", # ✅ Já está em Português
                    "location": self._extract_city_from_mention(mention),
                    "timestamp_utc": datetime.utcnow() - timedelta(days=random.randint(1, 15)),
                    "url": "https://social.com/seasonal_post"
                })
        
        # Menções típicas do período seco (junho a novembro)
        else:
            dry_mentions = [
                "Calor extremo em Balsas, mais de 40 graus!",
                "Falta de água em vários bairros de Codó",
                "Queimadas próximas a Imperatriz preocupam moradores",
                "Sistema de abastecimento de água em crise no interior"
            ]
            
            for mention in dry_mentions:
                seasonal_records.append({
                    "source_platform": "social_seasonal",
                    "theme": "Infraestrutura",
                    "text": f"{mention} [Tipo: Período Seco]",
                    "sentiment": "NEGATIVO", # ✅ Já está em Português
                    "location": self._extract_city_from_mention(mention),
                    "timestamp_utc": datetime.utcnow() - timedelta(days=random.randint(1, 15)),
                    "url": "https://social.com/seasonal_post"
                })
        
        return seasonal_records

    def collect_all_opinion_data(self):
        """Coleta todos os tipos de dados de opinião pública."""
        logger.info("Iniciando coleta completa de dados de opinião pública...")
        
        all_records = []
        
        try:
            # Coleta simulação do Google Reviews
            google_data = self.collect_google_reviews_simulation()
            all_records.extend(google_data)
            
            # Coleta menções de redes sociais
            social_data = self.collect_social_media_mentions()
            all_records.extend(social_data)
            
        except Exception as e:
            logger.error(f"Erro durante coleta de opinião pública: {e}")
        
        logger.info(f"Coleta de opinião pública finalizada. Total: {len(all_records)} registros")
        return all_records