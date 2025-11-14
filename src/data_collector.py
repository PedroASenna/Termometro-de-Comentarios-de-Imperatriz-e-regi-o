"""
Coletor de tweets usando a API v2 do Twitter (X).
"""
import tweepy
import logging
from datetime import datetime, timedelta, timezone
from src.config import LOCATION_SETTINGS

logger = logging.getLogger(__name__)

class TwitterCollector:
    def __init__(self, bearer_token):
        self.client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

    def collect(self, query, max_tweets=100):
        tweets_data = []
        try:
            location = f"point_radius:[{LOCATION_SETTINGS['longitude']} {LOCATION_SETTINGS['latitude']} {LOCATION_SETTINGS['radius']}]"
            full_query = f"({query}) {location} lang:pt -is:retweet"
            
            logger.info(f"Coletando com a query: {full_query}")

            response = self.client.search_recent_tweets(
                query=full_query,
                max_results=max_tweets,
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'text'],
                user_fields=['username', 'name', 'location'],
                expansions=['author_id']
            )

            if not response.data:
                return []

            users = {user["id"]: user for user in response.includes.get("users", [])}
            for tweet in response.data:
                user = users.get(tweet.author_id)
                tweets_data.append({
                    'id': tweet.id,
                    'data_criacao': tweet.created_at,
                    'usuario': user.username if user else 'N/A',
                    'nome_usuario': user.name if user else 'N/A',
                    'local_usuario': user.location if user else 'N/A',
                    'texto_original': tweet.text,
                    'retweets': tweet.public_metrics['retweet_count'],
                    'curtidas': tweet.public_metrics['like_count'],
                    'respostas': tweet.public_metrics['reply_count'],
                })
            return tweets_data

        except tweepy.errors.TooManyRequests:
            logger.warning("Limite de requisições da API atingido. Aguardando...")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado na coleta: {e}", exc_info=True)
            return []