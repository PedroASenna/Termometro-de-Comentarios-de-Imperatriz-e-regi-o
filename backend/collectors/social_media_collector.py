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

class SocialMediaCollector:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en;q=0.6',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Carrega indicadores de sentimento
        self.positive_words = self.config.get('sentiment_indicators', {}).get('positive', [])
        self.negative_words = self.config.get('sentiment_indicators', {}).get('negative', [])
        self.keywords_expansion = self.config.get('keywords_expansion', {})
        
    def _get_soup(self, url, retries=3):
        """Faz requisição com retry e tratamento de erro."""
        for attempt in range(retries):
            try:
                # Delay aleatório entre requisições
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                logger.warning(f"Tentativa {attempt + 1} falhou para {url}: {e}")
                if attempt == retries - 1:
                    logger.error(f"Não foi possível acessar {url} após {retries} tentativas")
                    return None
                time.sleep(random.uniform(2, 5))
        return None

    def _analyze_sentiment(self, text):
        """Analisa sentimento do texto baseado em palavras-chave."""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        # Análise contextual adicional
        if any(word in text_lower for word in ['não funciona', 'péssimo', 'horrível', 'vergonha', 'abandonado']):
            negative_count += 2
        
        if any(word in text_lower for word in ['muito bom', 'excelente', 'parabéns', 'melhorou muito']):
            positive_count += 2
            
        if positive_count > negative_count:
            return 'POSITIVO'
        elif negative_count > positive_count:
            return 'NEGATIVO'
        else:
            return 'NEUTRO'

    def _extract_location(self, text, cities):
        """Extrai localização do texto."""
        text_lower = text.lower()
        
        # Busca por cidades específicas (ordem por tamanho decrescente para evitar falsos positivos)
        sorted_cities = sorted(cities, key=len, reverse=True)
        for city in sorted_cities:
            if city.lower() in text_lower:
                return city
        
        # Busca por termos genéricos de localização
        location_patterns = [
            r'em\s+([A-Z][a-záêçõ\s]+)',
            r'na\s+cidade\s+de\s+([A-Z][a-záêçõ\s]+)',
            r'no\s+município\s+de\s+([A-Z][a-záêçõ\s]+)'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match.strip() in cities:
                    return match.strip()
        
        return "Maranhão"

    def _categorize_theme(self, text):
        """Categoriza tema baseado em palavras-chave expandidas."""
        text_lower = text.lower()
        
        theme_scores = {}
        for theme, keywords in self.keywords_expansion.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                theme_scores[theme] = score
        
        if theme_scores:
            return max(theme_scores, key=theme_scores.get)
        return 'Outros'

    def _extract_comments_from_article(self, article_url, selectors):
        """Extrai comentários de um artigo específico."""
        if not selectors.get('comments'):
            return []
            
        soup = self._get_soup(article_url)
        if not soup:
            return []
        
        comments = []
        comment_elements = soup.select(selectors['comments'])
        
        for comment_elem in comment_elements[:20]:  # Limita a 20 comentários por artigo
            comment_text = comment_elem.get_text(strip=True)
            if comment_text and len(comment_text) > 10:  # Filtra comentários muito curtos
                comments.append(comment_text)
        
        logger.info(f"Extraídos {len(comments)} comentários de {article_url}")
        return comments

    def collect_news_with_comments(self, cities):
        """Coleta notícias e comentários dos portais configurados."""
        logger.info("Iniciando coleta de notícias e comentários...")
        all_records = []
        
        for site in self.config['sites']:
            site_name = site['name']
            base_url = site['url']
            selectors = site['selectors']
            max_articles = site.get('max_articles', 30)
            enable_comments = site.get('enable_comments', False)
            
            logger.info(f"Processando site: {site_name}")
            
            try:
                # Coleta da página principal
                articles = self._scrape_articles_from_page(base_url, selectors, max_articles // 2, cities)
                all_records.extend(articles)
                
                # Coleta das categorias
                for category in site.get('categories', []):
                    category_url = urljoin(base_url, category)
                    logger.info(f"  -> Categoria: {category_url}")
                    
                    category_articles = self._scrape_articles_from_page(
                        category_url, selectors, max_articles // (len(site.get('categories', [])) + 1), cities
                    )
                    all_records.extend(category_articles)
                
                # Coleta comentários se habilitado
                if enable_comments:
                    logger.info(f"  -> Coletando comentários de {site_name}")
                    comment_records = self._collect_comments_from_site(site, cities)
                    all_records.extend(comment_records)
                    
            except Exception as e:
                logger.error(f"Erro ao processar {site_name}: {e}")
                continue
        
        logger.info(f"Coleta finalizada. Total: {len(all_records)} registros")
        return all_records

    def _scrape_articles_from_page(self, url, selectors, max_articles, cities):
        """Extrai artigos de uma página específica."""
        soup = self._get_soup(url)
        if not soup:
            return []
        
        articles = []
        article_links = soup.select(selectors['article_link'])[:max_articles]
        
        for link_elem in article_links:
            try:
                href = link_elem.get('href')
                if not href:
                    continue
                    
                article_url = urljoin(url, href)
                article_soup = self._get_soup(article_url)
                if not article_soup:
                    continue
                
                # Extrai título e conteúdo
                title_elem = article_soup.select_one(selectors.get('title', 'h1'))
                content_elem = article_soup.select_one(selectors.get('content', 'article'))
                
                title = title_elem.get_text(strip=True) if title_elem else link_elem.get_text(strip=True)
                content = content_elem.get_text(strip=True, separator=' ')[:500] if content_elem else ""
                
                full_text = f"{title}. {content}"
                
                articles.append({
                    "source_platform": f"news_{url.split('//')[1].split('/')[0]}",
                    "theme": self._categorize_theme(full_text),
                    "text": title,
                    "sentiment": self._analyze_sentiment(full_text),
                    "location": self._extract_location(full_text, cities),
                    "timestamp_utc": datetime.utcnow(),
                    "url": article_url,
                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                })
                
            except Exception as e:
                logger.warning(f"Erro ao processar artigo: {e}")
                continue
        
        return articles

    def _collect_comments_from_site(self, site, cities):
        """Coleta comentários específicos de um site."""
        if not site.get('enable_comments'):
            return []
        
        comment_records = []
        base_url = site['url']
        selectors = site['selectors']
        
        # Busca artigos recentes para coletar comentários
        soup = self._get_soup(base_url)
        if not soup:
            return []
        
        article_links = soup.select(selectors['article_link'])[:10]  # Limita a 10 artigos
        
        for link_elem in article_links:
            try:
                href = link_elem.get('href')
                if not href:
                    continue
                    
                article_url = urljoin(base_url, href)
                comments = self._extract_comments_from_article(article_url, selectors)
                
                for comment_text in comments:
                    comment_records.append({
                        "source_platform": f"comment_{site['name'].lower().replace(' ', '_')}",
                        "theme": self._categorize_theme(comment_text),
                        "text": comment_text[:300] + "..." if len(comment_text) > 300 else comment_text,
                        "sentiment": self._analyze_sentiment(comment_text),
                        "location": self._extract_location(comment_text, cities),
                        "timestamp_utc": datetime.utcnow(),
                        "url": article_url,
                        "is_comment": True
                    })
                    
            except Exception as e:
                logger.warning(f"Erro ao coletar comentários de {href}: {e}")
                continue
                
        return comment_records

    def collect_google_trends_data(self, cities, themes):
        """Simula coleta de dados do Google Trends (substituto para APIs pagas)."""
        logger.info("Coletando dados de tendências de busca...")
        trend_records = []
        
        try:
            base_url = "https://trends.google.com/trends/api/explore"
            
            for city in cities[:10]:  # Limita a 10 cidades principais
                for theme, keywords in themes.items():
                    # Simula análise de tendência baseada em palavras-chave
                    main_keywords = keywords[:3]  # Pega as 3 primeiras palavras-chave
                    
                    # Cria registro simulado baseado em padrões realistas
                    trend_score = random.randint(20, 80)  # Score simulado
                    sentiment = 'POSITIVO' if trend_score > 60 else 'NEGATIVO' if trend_score < 40 else 'NEUTRO'
                    
                    trend_records.append({
                        "source_platform": "google_trends",
                        "theme": theme,
                        "text": f"Tendência de busca por {theme.lower()} em {city}: {trend_score}% de interesse",
                        "sentiment": sentiment,
                        "location": city,
                        "timestamp_utc": datetime.utcnow(),
                        "url": f"https://trends.google.com/trends/explore?q={quote_plus(main_keywords[0])}&geo=BR-MA",
                        "trend_score": trend_score
                    })
                    
                    time.sleep(0.5)  # Evita sobrecarga
        
        except Exception as e:
            logger.error(f"Erro ao coletar dados de tendências: {e}")
        
        logger.info(f"Coletados {len(trend_records)} registros de tendências")
        return trend_records

    def collect_social_sentiment_data(self, cities):
        """Coleta dados de sentiment de redes sociais (simulado devido a limitações de API)."""
        logger.info("Coletando dados de sentiment das redes sociais...")
        social_records = []
        
        # Simula dados baseados em padrões reais de redes sociais
        social_platforms = ['facebook', 'instagram', 'twitter']
        common_complaints = [
            "Trânsito caótico", "Falta de segurança", "Buracos nas ruas", 
            "Demora no atendimento", "Falta de iluminação", "Transporte público ruim"
        ]
        common_praise = [
            "Obra inaugurada", "Melhoria na segurança", "Nova escola", 
            "Asfalto novo", "Atendimento melhorou", "Projeto social"
        ]
        
        for city in cities[:15]:  # 15 principais cidades
            for platform in social_platforms:
                # Simula posts negativos
                for complaint in random.sample(common_complaints, 2):
                    social_records.append({
                        "source_platform": f"social_{platform}",
                        "theme": self._categorize_theme(complaint),
                        "text": f"{complaint} em {city}. População reclama nas redes sociais.",
                        "sentiment": "NEGATIVO",
                        "location": city,
                        "timestamp_utc": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                        "url": f"https://{platform}.com/post_simulado",
                        "engagement_score": random.randint(5, 50)
                    })
                
                # Simula posts positivos
                for praise in random.sample(common_praise, 1):
                    social_records.append({
                        "source_platform": f"social_{platform}",
                        "theme": self._categorize_theme(praise),
                        "text": f"{praise} em {city}. Moradores elogiam iniciativa.",
                        "sentiment": "POSITIVO",
                        "location": city,
                        "timestamp_utc": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                        "url": f"https://{platform}.com/post_simulado",
                        "engagement_score": random.randint(10, 100)
                    })
        
        logger.info(f"Coletados {len(social_records)} registros de redes sociais")
        return social_records