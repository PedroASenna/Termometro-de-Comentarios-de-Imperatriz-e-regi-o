#!/usr/bin/env python3
"""
Script de configuração do Termômetro do Maranhão
Configura o ambiente, cria estrutura de diretórios e arquivos necessários
"""

import os
import json
import sys
import shutil
from pathlib import Path

def create_directory_structure():
    """Cria estrutura de diretórios necessária."""
    directories = [
        "backend",
        "backend/collectors",
        "frontend",
        "frontend/css",
        "frontend/js",
        "data",
        "logs"
    ]
    
    print("Criando estrutura de diretórios...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}/")

def create_config_files():
    """Cria arquivos de configuração necessários."""
    print("Criando arquivos de configuração...")
    
    # Arquivo de configuração para scrapers (já criado anteriormente)
    scrapers_config = {
        "sites": [
            {
                "name": "G1 Maranhão",
                "url": "https://g1.globo.com/ma/maranhao/",
                "categories": ["noticia/politica/", "noticia/economia/", "noticia/seguranca/", "noticia/cidades/"],
                "selectors": { 
                    "article_link": "a.feed-post-link", 
                    "title": "h1.content-head__title", 
                    "content": "article.content-text",
                    "comments": ".comments-list .comment-body"
                },
                "enable_comments": True,
                "max_articles": 50
            },
            {
                "name": "Imirante",
                "url": "https://imirante.com/",
                "categories": ["noticias/sao-luis/", "noticias/policia/", "noticias/economia/", "noticias/interior/"],
                "selectors": { 
                    "article_link": "a.list-item__title", 
                    "title": "h1.article-header__title", 
                    "content": "div.article-content",
                    "comments": ".comments .comment-content"
                },
                "enable_comments": True,
                "max_articles": 50
            },
            {
                "name": "Jornal Pequeno",
                "url": "https://www.jornalpequeno.com.br/",
                "categories": ["category/policia/", "category/economia/", "category/politica/", "category/cidades/"],
                "selectors": { 
                    "article_link": "h3.entry-title a", 
                    "title": "h1.entry-title", 
                    "content": "div.entry-content",
                    "comments": ".comment-content p"
                },
                "enable_comments": True,
                "max_articles": 40
            }
        ],
        "keywords_expansion": {
            "Segurança": ["policia", "crime", "assalto", "roubo", "homicidio", "violencia"],
            "Infraestrutura": ["rua", "buraco", "asfalto", "ponte", "obra", "saneamento"],
            "Comércio": ["preco", "comercio", "supermercado", "loja", "consumidor"],
            "Saúde": ["hospital", "posto", "sus", "medico", "consulta"],
            "Educação": ["escola", "professor", "aluno", "ensino", "universidade"],
            "Transporte": ["onibus", "transporte", "terminal", "passagem", "transito"]
        }
    }
    
    with open('scrapers_config.json', 'w', encoding='utf-8') as f:
        json.dump(scrapers_config, f, ensure_ascii=False, indent=2)
    print("  ✓ scrapers_config.json")
    
    # Arquivo de configuração do banco de dados
    database_config = """
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL do banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./termometro_ma.db"

# Criar engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Criar SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()
"""
    
    with open('backend/database.py', 'w', encoding='utf-8') as f:
        f.write(database_config)
    print("  ✓ backend/database.py")
    
    # Arquivo de modelos do banco
    models_config = """
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base

class Mention(Base):
    __tablename__ = "mentions"

    id = Column(Integer, primary_key=True, index=True)
    source_platform = Column(String, index=True)
    theme = Column(String, index=True)
    text = Column(Text)
    sentiment = Column(String, index=True)
    location = Column(String, index=True)
    timestamp_utc = Column(DateTime)
    url = Column(String)
"""
    
    with open('backend/models.py', 'w', encoding='utf-8') as f:
        f.write(models_config)
    print("  ✓ backend/models.py")
    
    # Arquivo CRUD
    crud_config = """
from sqlalchemy.orm import Session
from . import models
from datetime import datetime

def create_mention(db: Session, mention_data: dict):
    db_mention = models.Mention(
        source_platform=mention_data.get('source_platform'),
        theme=mention_data.get('theme'),
        text=mention_data.get('text'),
        sentiment=mention_data.get('sentiment'),
        location=mention_data.get('location'),
        timestamp_utc=mention_data.get('timestamp_utc', datetime.utcnow()),
        url=mention_data.get('url')
    )
    db.add(db_mention)
    db.commit()
    db.refresh(db_mention)
    return db_mention

def get_mentions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Mention).offset(skip).limit(limit).all()

def get_mentions_by_city(db: Session, city: str):
    return db.query(models.Mention).filter(models.Mention.location == city).all()
"""
    
    with open('backend/crud.py', 'w', encoding='utf-8') as f:
        f.write(crud_config)
    print("  ✓ backend/crud.py")
    
    # Arquivo __init__.py para o backend
    with open('backend/__init__.py', 'w') as f:
        f.write("")
    print("  ✓ backend/__init__.py")
    
    with open('backend/collectors/__init__.py', 'w') as f:
        f.write("")
    print("  ✓ backend/collectors/__init__.py")

def create_sample_geojson():
    """Cria um arquivo GeoJSON de exemplo com cidades do Maranhão."""
    print("Criando arquivo GeoJSON de exemplo...")
    
    sample_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "São Luís"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-44.3, -2.4], [-44.1, -2.4], [-44.1, -2.6], [-44.3, -2.6], [-44.3, -2.4]]]
                }
            },
            {
                "type": "Feature", 
                "properties": {"name": "Imperatriz"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-47.6, -5.4], [-47.4, -5.4], [-47.4, -5.6], [-47.6, -5.6], [-47.6, -5.4]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Caxias"},
                "geometry": {
                    "type": "Polygon", 
                    "coordinates": [[[-43.4, -4.7], [-43.2, -4.7], [-43.2, -4.9], [-43.4, -4.9], [-43.4, -4.7]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Codó"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-43.9, -4.4], [-43.7, -4.4], [-43.7, -4.6], [-43.9, -4.6], [-43.9, -4.4]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Timon"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-42.9, -5.0], [-42.7, -5.0], [-42.7, -5.2], [-42.9, -5.2], [-42.9, -5.0]]]
                }
            }
        ]
    }
    
    with open('ma_cities.geojson', 'w', encoding='utf-8') as f:
        json.dump(sample_geojson, f, ensure_ascii=False, indent=2)
    print("  ✓ ma_cities.geojson")

def create_requirements():
    """Cria arquivo requirements.txt."""
    print("Criando arquivo requirements.txt...")
    
    requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pandas==2.1.3
requests==2.31.0
beautifulsoup4==4.12.2
openpyxl==3.1.2
python-multipart==0.0.6
aiofiles==0.22.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("  ✓ requirements.txt")

def create_readme():
    """Cria arquivo README com instruções."""
    print("Criando README.md...")
    
    readme_content = """# Termômetro do Maranhão

Sistema de monitoramento da satisfação popular no estado do Maranhão através da análise de dados de múltiplas fontes.

## 🚀 Instalação e Configuração

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar Coletores de Dados
```bash
python run_collectors.py
```

### 3. Iniciar API Backend
```bash
python -m uvicorn backend.main:app --reload
```

### 4. Abrir Frontend
Abra o arquivo `frontend/index.html` no navegador.

## 📊 Fontes de Dados

- **IBGE**: Dados socioeconômicos oficiais
- **Fórum Brasileiro de Segurança Pública**: Dados de criminalidade
- **Portais de Notícias**: G1 Maranhão, Imirante, Jornal Pequeno
- **Redes Sociais**: Análise de sentimento simulada
- **Opinião Pública**: Reclame Aqui e reviews simulados

## 🎯 Funcionalidades

- Mapa interativo do Maranhão
- Termômetro visual de satisfação
- Análise de sentimento automática
- Categorização temática
- Filtros por cidade e tema
- Dashboard em tempo real

## 🛠️ Estrutura do Projeto

```
termometro_ma/
├── backend/
│   ├── collectors/
│   ├── main.py
│   ├── models.py
│   └── crud.py
├── frontend/
│   ├── css/style.css
│   ├── js/app.js
│   └── index.html
├── ma_cities.geojson
├── scrapers_config.json
└── run_collectors.py
```

## 🔧 Configuração Avançada

Edite `scrapers_config.json` para adicionar novos sites ou modificar seletores CSS.

## 📈 Análise de Dados

O sistema categoriza automaticamente os dados em:
- Segurança
- Infraestrutura
- Saúde
- Educação
- Transporte
- Comércio
- Administração Pública

Sentimentos são classificados como: POSITIVO, NEGATIVO ou NEUTRO.
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("  ✓ README.md")

def main():
    """Executa configuração completa do sistema."""
    print("=" * 60)
    print("🌡️  CONFIGURANDO TERMÔMETRO DO MARANHÃO")
    print("=" * 60)
    
    try:
        create_directory_structure()
        print()
        create_config_files()
        print()
        create_sample_geojson()
        print()
        create_requirements()
        print()
        create_readme()
        
        print("\n" + "=" * 60)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. pip install -r requirements.txt")
        print("2. Coloque seus arquivos existentes nas pastas correspondentes:")
        print("   - backend/collectors/ (seus coletores)")
        print("   - backend/main.py (sua API)")
        print("   - frontend/ (seus arquivos HTML/CSS/JS)")
        print("3. python run_collectors.py")
        print("4. python -m uvicorn backend.main:app --reload")
        print("\n🎉 Sistema pronto para uso!")
        
    except Exception as e:
        print(f"❌ Erro durante a configuração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()