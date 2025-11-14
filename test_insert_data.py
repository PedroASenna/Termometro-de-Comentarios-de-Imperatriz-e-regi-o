"""
Script para inserir dados de teste no banco
Execute: python test_insert_data.py
"""

from backend.database import SessionLocal
from backend.crud import create_mention
from datetime import datetime, timedelta
import random

def insert_test_data():
    db = SessionLocal()
    
    print("🔧 Inserindo dados de teste...")
    
    # Dados de teste variados
    test_data = [
        {
            "source_platform": "IBGE",
            "theme": "Economia",
            "text": "PIB per capita em São Luís: R$ 25.000",
            "sentiment": "NEUTRO",
            "location": "São Luís",
            "timestamp_utc": datetime.utcnow() - timedelta(days=5),
            "url": "https://ibge.gov.br"
        },
        {
            "source_platform": "news_g1",
            "theme": "Saúde",
            "text": "Novo hospital inaugurado em Imperatriz",
            "sentiment": "POSITIVO",
            "location": "Imperatriz",
            "timestamp_utc": datetime.utcnow() - timedelta(days=2),
            "url": "https://g1.globo.com"
        },
        {
            "source_platform": "reclame_aqui",
            "theme": "Transporte",
            "text": "Ônibus lotado em Caxias, péssimo serviço",
            "sentiment": "NEGATIVO",
            "location": "Caxias",
            "timestamp_utc": datetime.utcnow() - timedelta(days=1),
            "url": "https://reclameaqui.com.br"
        },
        {
            "source_platform": "social_facebook",
            "theme": "Infraestrutura",
            "text": "Buracos na rua principal de Timon",
            "sentiment": "NEGATIVO",
            "location": "Timon",
            "timestamp_utc": datetime.utcnow(),
            "url": "https://facebook.com"
        },
        {
            "source_platform": "IBGE_Demografia",
            "theme": "Demografia",
            "text": "População estimada de Codó: 120.000 habitantes",
            "sentiment": "NEUTRO",
            "location": "Codó",
            "timestamp_utc": datetime.utcnow() - timedelta(days=10),
            "url": "https://cidades.ibge.gov.br"
        },
        {
            "source_platform": "google_reviews",
            "theme": "Educação",
            "text": "Escola estadual melhorou muito o atendimento",
            "sentiment": "POSITIVO",
            "location": "São Luís",
            "timestamp_utc": datetime.utcnow() - timedelta(days=7),
            "url": "https://google.com/maps"
        },
        {
            "source_platform": "news_imirante",
            "theme": "Segurança",
            "text": "Assalto em Bacabal preocupa moradores",
            "sentiment": "NEGATIVO",
            "location": "Bacabal",
            "timestamp_utc": datetime.utcnow() - timedelta(days=3),
            "url": "https://imirante.com"
        },
        {
            "source_platform": "IBGE",
            "theme": "Economia",
            "text": "PIB de Imperatriz cresceu 5% em 2023",
            "sentiment": "POSITIVO",
            "location": "Imperatriz",
            "timestamp_utc": datetime.utcnow() - timedelta(days=15),
            "url": "https://ibge.gov.br"
        },
        {
            "source_platform": "social_twitter",
            "theme": "Administração Pública",
            "text": "Prefeitura de Balsas anuncia novas obras",
            "sentiment": "NEUTRO",
            "location": "Balsas",
            "timestamp_utc": datetime.utcnow() - timedelta(days=4),
            "url": "https://twitter.com"
        },
        {
            "source_platform": "reclame_aqui",
            "theme": "Infraestrutura",
            "text": "CEMAR demora para restabelecer energia",
            "sentiment": "NEGATIVO",
            "location": "São Luís",
            "timestamp_utc": datetime.utcnow() - timedelta(hours=12),
            "url": "https://reclameaqui.com.br"
        }
    ]
    
    # Adiciona mais registros variados
    cities = ["São Luís", "Imperatriz", "Caxias", "Timon", "Codó", "Bacabal", "Balsas", "Santa Inês"]
    themes = ["Saúde", "Educação", "Transporte", "Segurança", "Infraestrutura", "Economia"]
    sentiments = ["POSITIVO", "NEGATIVO", "NEUTRO"]
    sources = ["IBGE", "news_g1", "social_facebook", "reclame_aqui", "google_reviews"]
    
    # Gera 40 registros adicionais aleatórios
    for i in range(40):
        test_data.append({
            "source_platform": random.choice(sources),
            "theme": random.choice(themes),
            "text": f"Registro de teste {i+1} para análise de dados",
            "sentiment": random.choice(sentiments),
            "location": random.choice(cities),
            "timestamp_utc": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            "url": f"https://example.com/test{i+1}"
        })
    
    # Insere no banco
    count = 0
    for record in test_data:
        try:
            create_mention(db, record)
            count += 1
        except Exception as e:
            print(f"❌ Erro ao inserir registro: {e}")
    
    db.close()
    
    print(f"✅ {count}/{len(test_data)} registros de teste inseridos com sucesso!")
    print("\n🎯 Agora teste novamente:")
    print("1. http://localhost:8000/api/data/analysis")
    print("2. http://localhost:8000/api/data/comparison-tables")
    print("3. Abra o frontend: templates/fonte_de_dados.html")

if __name__ == "__main__":
    insert_test_data()