"""
Módulo de autenticação com a API do Twitter
"""
import tweepy
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

def authenticate_twitter():
    """
    Autentica com a API do Twitter usando as chaves do .env
    
    Returns:
        tweepy.API: Objeto da API autenticado ou None em caso de falha
    """
    load_dotenv()
    
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
    BEARER_TOKEN = os.getenv("BEARER_TOKEN")
    
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        logger.error("Credenciais da API não encontradas no arquivo .env")
        return None
    
    try:
        # Autenticação com OAuth 1.0a (para operações de leitura/gravação)
        auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        
        # Criar objeto API
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # Verificar credenciais
        api.verify_credentials()
        logger.info("Autenticação com a API do Twitter realizada com sucesso!")
        
        return api
        
    except Exception as e:
        logger.error(f"Erro na autenticação com a API do Twitter: {str(e)}")
        return None