import logging
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.scraped_urls = set()

    def _get_soup(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Não foi possível buscar a URL {url}: {e}")
            return None

    def _scrape_page(self, url, selectors):
        page_articles = []
        soup = self._get_soup(url)
        if not soup:
            return []

        article_links = soup.select(selectors['article_link'])
        for link_tag in article_links:
            href = link_tag.get('href')
            if not href: continue
            
            article_url = urljoin(url, href)
            if article_url in self.scraped_urls: continue
            
            self.scraped_urls.add(article_url)
            
            article_soup = self._get_soup(article_url)
            if not article_soup: continue

            title = (article_soup.select_one(selectors['title']) or link_tag).get_text(strip=True)
            content = (article_soup.select_one(selectors['content']) or BeautifulSoup("<p></p>", "html.parser")).get_text(strip=True, separator=' ')
            
            page_articles.append({
                "id": f"news_{len(self.scraped_urls)}",
                "type": "news_article",
                "text": f"{title}. {content}",
                "author": self.current_site_name,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {"title": title, "url": article_url}
            })
        return page_articles

    def scrape_all_sites(self):
        logger.info("Iniciando scraping de portais de notícias.")
        all_articles = []

        for site in self.config['sites']:
            self.current_site_name = site['name']
            base_url = site['url']
            selectors = site['selectors']
            logger.info(f"Processando site: {self.current_site_name}")

            all_articles.extend(self._scrape_page(base_url, selectors))

            if "categories" in site:
                for category_path in site.get("categories", []):
                    category_url = urljoin(base_url, category_path)
                    logger.info(f"---> Raspando categoria: {category_url}")
                    all_articles.extend(self._scrape_page(category_url, selectors))

        logger.info(f"Scraping de notícias finalizado. Total de {len(all_articles)} artigos únicos coletados.")
        return all_articles