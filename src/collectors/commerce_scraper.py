import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

logger = logging.getLogger(__name__)

class CommerceScraper:
    def __init__(self, target_url):
        self.target_url = target_url
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.implicitly_wait(10)

    def scrape_procon_itz(self):
        logger.info(f"Iniciando scraper especializado para: {self.target_url}")
        all_articles = []
        try:
            self.driver.get(self.target_url)
            time.sleep(random.uniform(3, 5))

            # Os seletores aqui são específicos para a página de notícias do PROCON de Imperatriz
            links = self.driver.find_elements(By.CSS_SELECTOR, "a.post-item")
            article_urls = [link.get_attribute('href') for link in links[:5]] # Pega as 5 primeiras notícias

            for url in article_urls:
                self.driver.get(url)
                time.sleep(random.uniform(2, 4))
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                title = soup.select_one("h1.post-title").get_text(strip=True)
                content = soup.select_one("div.post-content").get_text(strip=True, separator=' ')

                all_articles.append({
                    "id": f"procon_itz_{len(all_articles)}",
                    "type": "gov_news",
                    "text": f"{title}. {content}",
                    "author": "PROCON Imperatriz",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"title": title, "url": url}
                })
            logger.info(f"Scraper do Procon finalizado. Coletou {len(all_articles)} notícias.")
        except Exception as e:
            logger.error(f"Erro no scraper do Procon: {e}", exc_info=True)
        finally:
            self.driver.quit()
        
        return all_articles