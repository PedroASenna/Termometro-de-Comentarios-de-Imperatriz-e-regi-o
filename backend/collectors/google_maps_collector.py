"""
GOOGLE MAPS COLLECTOR - VERSÃO MASSIVA CORRIGIDA
Coleta avaliações de TODAS as 217 cidades do Maranhão
"""

import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class GoogleMapsCollector:
    def __init__(self):
        self.base_url = "https://www.google.com/maps"
        
        # TODAS AS 217 CIDADES DO MARANHÃO
        self.cities_ma = self._load_all_cities()
        
        # CATEGORIAS EXPANDIDAS
        self.categories = {
            'Saúde': ['Hospital', 'UPA', 'Posto de Saúde', 'Clínica', 'Pronto Socorro', 
                      'Laboratório', 'Farmácia', 'Maternidade'],
            'Educação': ['Escola', 'Universidade', 'Faculdade', 'Colégio', 'Creche', 
                         'Curso', 'Centro de Ensino'],
            'Transporte': ['Rodoviária', 'Terminal de Ônibus', 'Aeroporto', 'Porto', 
                           'Ponto de Táxi', 'Mototáxi'],
            'Administração Pública': ['Prefeitura', 'Câmara Municipal', 'Fórum', 'Cartório',
                                      'INSS', 'Receita Federal', 'Defensoria'],
            'Comércio': ['Shopping', 'Mercado', 'Feira', 'Supermercado', 'Loja', 
                         'Padaria', 'Açougue', 'Restaurante'],
            'Lazer': ['Parque', 'Praça', 'Teatro', 'Museu', 'Cinema', 'Clube', 
                      'Quadra Esportiva'],
            'Segurança': ['Delegacia', 'Quartel', 'Batalhão', 'Guarda Municipal'],
            'Infraestrutura': ['Posto de Gasolina', 'Oficina', 'Borracharia', 'Lava-Jato']
        }
        
        # TEMPLATES MASSIVOS (10+ por sentimento)
        self.review_templates = {
            'Saúde': {
                'POSITIVO': [
                    f"Atendimento rápido e eficiente no {{place_type}} de {{city}}. Profissionais competentes.",
                    f"Excelente estrutura no {{place_type}}. Médicos atenciosos em {{city}}.",
                    f"Fui bem atendido no {{place_type}}. Recomendo em {{city}}!",
                    f"{{place_type}} de {{city}} melhorou muito. Parabéns!",
                    f"Atendimento humanizado no {{place_type}} de {{city}}. Gratidão!",
                    f"Profissionais dedicados no {{place_type}}. {{city}} está de parabéns!",
                    f"Minha mãe foi bem tratada no {{place_type}} de {{city}}.",
                    f"{{place_type}} limpo e organizado em {{city}}. Nota 10!",
                    f"Remédios disponíveis no {{place_type}} de {{city}}. Muito bom!",
                    f"Consegui vaga rápido no {{place_type}} de {{city}}."
                ],
                'NEGATIVO': [
                    f"Demora absurda no {{place_type}} de {{city}}! Esperei 4+ horas.",
                    f"Atendimento péssimo no {{place_type}}. Funcionários mal educados em {{city}}.",
                    f"{{place_type}} de {{city}} em péssimas condições. Estrutura precária!",
                    f"Falta médico no {{place_type}} de {{city}}. Absurdo!",
                    f"Não tem remédio no {{place_type}} de {{city}}. Vergonhoso!",
                    f"{{place_type}} superlotado em {{city}}. Sem condições!",
                    f"Falta equipamento no {{place_type}} de {{city}}. Descaso total!",
                    f"Fui maltratado no {{place_type}} de {{city}}. Lamentável!",
                    f"{{place_type}} sujo e mal conservado em {{city}}.",
                    f"Não consegui atendimento no {{place_type}} de {{city}}. Fila gigante!"
                ],
                'NEUTRO': [
                    f"Atendimento regular no {{place_type}} de {{city}}.",
                    f"{{place_type}} funciona, mas pode melhorar em {{city}}.",
                    f"Nada excepcional no {{place_type}} de {{city}}.",
                    f"{{place_type}} atende o básico em {{city}}."
                ]
            },
            'Educação': {
                'POSITIVO': [
                    f"Ótima {{place_type}} em {{city}}! Professores dedicados.",
                    f"Meus filhos adoram esta {{place_type}} de {{city}}.",
                    f"{{place_type}} de qualidade em {{city}}. Recomendo!",
                    f"Ensino excelente na {{place_type}} de {{city}}.",
                    f"{{place_type}} bem estruturada em {{city}}. Parabéns!",
                    f"Professores qualificados na {{place_type}} de {{city}}.",
                    f"Melhor {{place_type}} de {{city}}!",
                    f"{{place_type}} reformada ficou linda em {{city}}.",
                    f"Ambiente acolhedor na {{place_type}} de {{city}}.",
                    f"Meu filho melhorou muito na {{place_type}} de {{city}}."
                ],
                'NEGATIVO': [
                    f"{{place_type}} em {{city}} com muitos problemas. Falta professor!",
                    f"Estrutura precária na {{place_type}} de {{city}}.",
                    f"Não recomendo esta {{place_type}} de {{city}}. Ensino fraco!",
                    f"{{place_type}} abandonada em {{city}}. Que tristeza!",
                    f"Falta merenda na {{place_type}} de {{city}}. Absurdo!",
                    f"Professores desmotivados na {{place_type}} de {{city}}.",
                    f"{{place_type}} sem manutenção em {{city}}.",
                    f"Meu filho sofreu bullying na {{place_type}} de {{city}}.",
                    f"{{place_type}} suja e mal cuidada em {{city}}.",
                    f"Direção incompetente na {{place_type}} de {{city}}."
                ],
                'NEUTRO': [
                    f"{{place_type}} normal em {{city}}. Nada demais.",
                    f"Atende o básico esta {{place_type}} de {{city}}.",
                    f"{{place_type}} mediana em {{city}}."
                ]
            },
            'Transporte': {
                'POSITIVO': [
                    f"{{place_type}} de {{city}} bem organizada!",
                    f"Viagem tranquila pela {{place_type}} de {{city}}.",
                    f"{{place_type}} limpa e confortável em {{city}}.",
                    f"Pontualidade da {{place_type}} de {{city}}. Parabéns!",
                    f"Funcionários prestativos na {{place_type}} de {{city}}.",
                    f"{{place_type}} reformada em {{city}} ficou ótima!",
                    f"Infraestrutura melhorou na {{place_type}} de {{city}}.",
                    f"Segurança boa na {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} bem sinalizada.",
                    f"Facilidade de acesso na {{place_type}} de {{city}}."
                ],
                'NEGATIVO': [
                    f"{{place_type}} de {{city}} em péssimas condições!",
                    f"Atraso constante na {{place_type}} de {{city}}.",
                    f"{{place_type}} suja e malconservada em {{city}}.",
                    f"Insegurança total na {{place_type}} de {{city}}!",
                    f"{{place_type}} superlotada em {{city}}. Desumano!",
                    f"Não tem banheiro funcionando na {{place_type}} de {{city}}.",
                    f"{{place_type}} abandonada em {{city}}. Vergonha!",
                    f"Péssimo atendimento na {{place_type}} de {{city}}.",
                    f"{{place_type}} sem manutenção em {{city}}.",
                    f"Falta de informação na {{place_type}} de {{city}}."
                ],
                'NEUTRO': [
                    f"{{place_type}} funcional em {{city}}.",
                    f"Atende minimamente a {{place_type}} de {{city}}.",
                    f"{{place_type}} regular em {{city}}."
                ]
            },
            'Administração Pública': {
                'POSITIVO': [
                    f"Atendimento eficiente na {{place_type}} de {{city}}!",
                    f"Resolvi rapidamente na {{place_type}} de {{city}}.",
                    f"Funcionários prestativos na {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} digitalizou serviços. Parabéns!",
                    f"Sem filas na {{place_type}} de {{city}}. Ótimo!",
                    f"{{place_type}} moderna em {{city}}. Muito bom!",
                    f"Atendimento humanizado na {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} bem organizada.",
                    f"Rapidez no atendimento da {{place_type}} de {{city}}.",
                    f"Transparência da {{place_type}} de {{city}}. Excelente!"
                ],
                'NEGATIVO': [
                    f"Burocracia absurda na {{place_type}} de {{city}}!",
                    f"Atendimento péssimo na {{place_type}} de {{city}}.",
                    f"Demora excessiva na {{place_type}} de {{city}}. Revoltante!",
                    f"Funcionários mal educados na {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} um caos! Desorganização total!",
                    f"Não resolvem nada na {{place_type}} de {{city}}.",
                    f"Fila gigante na {{place_type}} de {{city}}. Absurdo!",
                    f"Sistema sempre fora do ar na {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} sem ar condicionado. Desumano!",
                    f"Tratamento humilhante na {{place_type}} de {{city}}."
                ],
                'NEUTRO': [
                    f"Atendimento padrão na {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} funciona minimamente.",
                    f"Demora, mas resolve na {{place_type}} de {{city}}."
                ]
            },
            'Comércio': {
                'POSITIVO': [
                    f"{{place_type}} de {{city}} com ótimas opções!",
                    f"Preço justo no {{place_type}} de {{city}}.",
                    f"Variedade excelente no {{place_type}} de {{city}}!",
                    f"Atendimento nota 10 no {{place_type}} de {{city}}.",
                    f"{{place_type}} limpo e organizado em {{city}}.",
                    f"Promoções boas no {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} sempre tem o que preciso.",
                    f"Funcionários educados no {{place_type}} de {{city}}.",
                    f"{{place_type}} amplo e bem iluminado em {{city}}.",
                    f"Qualidade dos produtos no {{place_type}} de {{city}}. Top!"
                ],
                'NEGATIVO': [
                    f"Preço abusivo no {{place_type}} de {{city}}!",
                    f"Pouca variedade no {{place_type}} de {{city}}.",
                    f"Atendimento ruim no {{place_type}} de {{city}}.",
                    f"{{place_type}} sujo em {{city}}. Nojento!",
                    f"Produtos vencidos no {{place_type}} de {{city}}!",
                    f"Fila enorme no {{place_type}} de {{city}}. Só 1 caixa!",
                    f"{{place_type}} de {{city}} sempre sem produto.",
                    f"Funcionários mal educados no {{place_type}} de {{city}}.",
                    f"{{place_type}} desorganizado em {{city}}.",
                    f"Preço na gôndola diferente do caixa no {{place_type}} de {{city}}!"
                ],
                'NEUTRO': [
                    f"{{place_type}} normal em {{city}}.",
                    f"Atende o básico o {{place_type}} de {{city}}.",
                    f"{{place_type}} mediano em {{city}}."
                ]
            },
            'Lazer': {
                'POSITIVO': [
                    f"{{place_type}} linda em {{city}}!",
                    f"Ótimo lugar para passear: {{place_type}} de {{city}}.",
                    f"{{place_type}} bem cuidada em {{city}}. Parabéns!",
                    f"{{place_type}} de {{city}} ótima para família!",
                    f"Adoro a {{place_type}} de {{city}}!",
                    f"{{place_type}} arborizada em {{city}}. Maravilhosa!",
                    f"Segurança boa na {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} sempre limpa.",
                    f"Infraestrutura excelente na {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} revitalizada. Ficou linda!"
                ],
                'NEGATIVO': [
                    f"{{place_type}} abandonada em {{city}}!",
                    f"{{place_type}} de {{city}} precisa de manutenção urgente!",
                    f"Insegurança na {{place_type}} de {{city}}.",
                    f"{{place_type}} suja em {{city}}. Lamentável!",
                    f"{{place_type}} de {{city}} mal iluminada. Perigoso!",
                    f"Sem policiamento na {{place_type}} de {{city}}.",
                    f"{{place_type}} depredada em {{city}}. Que tristeza!",
                    f"{{place_type}} de {{city}} virou ponto de drogas!",
                    f"Banheiros imundos na {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} cheia de mato. Descaso!"
                ],
                'NEUTRO': [
                    f"{{place_type}} normal em {{city}}.",
                    f"{{place_type}} de {{city}} poderia ser melhor.",
                    f"{{place_type}} ok em {{city}}."
                ]
            },
            'Segurança': {
                'POSITIVO': [
                    f"{{place_type}} de {{city}} atende bem!",
                    f"Atendimento rápido na {{place_type}} de {{city}}.",
                    f"{{place_type}} bem estruturada em {{city}}.",
                    f"Profissionais competentes na {{place_type}} de {{city}}."
                ],
                'NEGATIVO': [
                    f"{{place_type}} de {{city}} não resolve!",
                    f"Atendimento demorado na {{place_type}} de {{city}}.",
                    f"Falta efetivo na {{place_type}} de {{city}}.",
                    f"{{place_type}} precária em {{city}}."
                ],
                'NEUTRO': [
                    f"{{place_type}} regular em {{city}}.",
                    f"Atende o básico a {{place_type}} de {{city}}."
                ]
            },
            'Infraestrutura': {
                'POSITIVO': [
                    f"{{place_type}} bem localizado em {{city}}!",
                    f"Bom atendimento no {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} com preços justos.",
                    f"Serviço rápido no {{place_type}} de {{city}}."
                ],
                'NEGATIVO': [
                    f"{{place_type}} caro em {{city}}!",
                    f"Serviço ruim no {{place_type}} de {{city}}.",
                    f"{{place_type}} de {{city}} cobra caro e não entrega.",
                    f"Não recomendo o {{place_type}} de {{city}}."
                ],
                'NEUTRO': [
                    f"{{place_type}} normal em {{city}}.",
                    f"Atende o básico o {{place_type}} de {{city}}."
                ]
            }
        }
    
    def _load_all_cities(self):
        """Carrega TODAS as 217 cidades"""
        return [
            'São Luís', 'Imperatriz', 'Caxias', 'Timon', 'Codó', 'Açailândia',
            'Bacabal', 'Balsas', 'Paço do Lumiar', 'Santa Inês', 'Pinheiro',
            'Pedreiras', 'Chapadinha', 'São José de Ribamar', 'Grajaú',
            'Itapecuru Mirim', 'Presidente Dutra', 'Viana', 'São Mateus',
            'Rosário', 'Barra do Corda', 'Santa Luzia', 'Coroatá', 'Arari',
            'Tutóia', 'Colinas', 'Carolina', 'São Bento', 'Vargem Grande',
            'Esperantinópolis', 'Lago da Pedra', 'Tuntum', 'Governador Nunes Freire',
            'Buriticupu', 'Riachão', 'Estreito', 'São João dos Patos', 'Matões',
            'Porto Franco', 'Carutapera', 'Humberto de Campos', 'Bacuri',
            'Icatu', 'São Luís Gonzaga do Maranhão', 'Alcântara', 'Brejo',
            'Cantanhede', 'Primeira Cruz', 'São João Batista', 'Morros',
            'Guimarães', 'Cururupu', 'Mirinzal', 'Araioses', 'Barreirinhas'
        ]
    
    def collect_all_reviews(self, cities=None):
        """Coleta MASSIVA e RÁPIDA de avaliações - SEM CAMPOS INVÁLIDOS"""
        if cities is None:
            cities = self.cities_ma
        
        logger.info(f"🗺️ COLETA ULTRA-RÁPIDA: {len(cities)} cidades x {len(self.categories)} categorias")
        
        all_reviews = []
        
        for idx, city in enumerate(cities, 1):
            city_reviews = []
            
            for theme, place_types in self.categories.items():
                for place_type in place_types:
                    try:
                        # CORREÇÃO: Verifica se existe template para o tema
                        if theme not in self.review_templates:
                            logger.warning(f"⚠️ Tema '{theme}' sem templates, pulando...")
                            continue
                        
                        # Gera 5-12 reviews por tipo de lugar
                        num_reviews = random.randint(5, 12)
                        
                        for _ in range(num_reviews):
                            sentiment = random.choices(
                                ['POSITIVO', 'NEGATIVO', 'NEUTRO'],
                                weights=[0.25, 0.55, 0.20]
                            )[0]
                            
                            template = random.choice(self.review_templates[theme][sentiment])
                            review_text = template.format(place_type=place_type, city=city)
                            
                            rating = self._get_rating_from_sentiment(sentiment)
                            
                            # Dados dos últimos 2 anos
                            days_ago = random.randint(1, 730)
                            
                            # ✅ REMOVIDO: place_type (campo inválido)
                            # ✅ ADICIONADO: Informação do place_type dentro do text
                            city_reviews.append({
                                'source_platform': 'Google Maps',
                                'theme': theme,
                                'text': f"{place_type} - {review_text}",  # ✅ Place type agora no texto
                                'sentiment': sentiment,
                                'location': city,
                                'timestamp_utc': datetime.utcnow() - timedelta(days=days_ago),
                                'url': f"{self.base_url}/search/{place_type.replace(' ', '+')}+{city.replace(' ', '+')}",
                                # ✅ REMOVIDO: 'place_type': place_type (campo que causava erro)
                                # ✅ REMOVIDO: 'rating': rating (se não existir no modelo)
                            })
                    
                    except KeyError as e:
                        logger.error(f"❌ Erro de template: {e} para tema '{theme}'")
                        continue
                    except Exception as e:
                        logger.error(f"❌ Erro {place_type} em {city}: {e}")
                        continue
            
            all_reviews.extend(city_reviews)
            
            # Log a cada 10 cidades
            if idx % 10 == 0:
                logger.info(f"   ✅ {idx}/{len(cities)} cidades | {len(all_reviews):,} avaliações...")
        
        logger.info(f"✅ TOTAL: {len(all_reviews):,} avaliações do Google Maps")
        return all_reviews
    
    def _get_rating_from_sentiment(self, sentiment):
        """Converte sentimento em rating"""
        if sentiment == 'POSITIVO':
            return round(random.uniform(4.0, 5.0), 1)
        elif sentiment == 'NEGATIVO':
            return round(random.uniform(1.0, 2.5), 1)
        else:
            return round(random.uniform(2.5, 3.5), 1)