"""
Script de diagnóstico para verificar o banco de dados
Execute: python debug_database.py
"""

import sys
import os

# Adiciona o diretório do projeto ao path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

print("="*60)
print("🔍 DIAGNÓSTICO DO BANCO DE DADOS")
print("="*60)

# 1. Verifica importações
print("\n[1/6] Verificando importações...")
try:
    from backend.database import SessionLocal, engine
    from backend.models import Base, Mention
    from backend.crud import create_mention
    print("✅ Importações OK")
except Exception as e:
    print(f"❌ Erro nas importações: {e}")
    sys.exit(1)

# 2. Verifica conexão com banco
print("\n[2/6] Verificando conexão com banco de dados...")
try:
    db = SessionLocal()
    print("✅ Conexão com banco OK")
except Exception as e:
    print(f"❌ Erro na conexão: {e}")
    sys.exit(1)

# 3. Verifica se as tabelas existem
print("\n[3/6] Verificando tabelas...")
try:
    # Cria tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas/verificadas")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
    sys.exit(1)

# 4. Conta registros existentes
print("\n[4/6] Contando registros existentes...")
try:
    count = db.query(Mention).count()
    print(f"📊 Total de registros no banco: {count}")
    
    if count > 0:
        print("\n📋 Amostra dos dados:")
        sample = db.query(Mention).limit(3).all()
        for i, m in enumerate(sample, 1):
            print(f"\n  Registro {i}:")
            print(f"    ID: {m.id}")
            print(f"    Fonte: {m.source_platform}")
            print(f"    Tema: {m.theme}")
            print(f"    Texto: {m.text[:50]}...")
            print(f"    Sentimento: {m.sentiment}")
            print(f"    Localização: {m.location}")
    else:
        print("⚠️  Banco vazio! Vamos inserir dados de teste...")
        
except Exception as e:
    print(f"❌ Erro ao contar registros: {e}")
    sys.exit(1)

# 5. Insere dados de teste se banco estiver vazio
if count == 0:
    print("\n[5/6] Inserindo dados de teste...")
    from datetime import datetime, timedelta
    
    test_records = [
        {
            "source_platform": "IBGE",
            "theme": "Economia",
            "text": "PIB per capita em São Luís: R$ 25.000",
            "sentiment": "NEUTRO",
            "location": "São Luís",
            "timestamp_utc": datetime.utcnow(),
            "url": "https://ibge.gov.br"
        },
        {
            "source_platform": "news_g1",
            "theme": "Saúde",
            "text": "Novo hospital inaugurado em Imperatriz",
            "sentiment": "POSITIVO",
            "location": "Imperatriz",
            "timestamp_utc": datetime.utcnow() - timedelta(days=1),
            "url": "https://g1.globo.com"
        },
        {
            "source_platform": "reclame_aqui",
            "theme": "Transporte",
            "text": "Ônibus lotado, péssimo atendimento",
            "sentiment": "NEGATIVO",
            "location": "Caxias",
            "timestamp_utc": datetime.utcnow() - timedelta(days=2),
            "url": "https://reclameaqui.com.br"
        },
        {
            "source_platform": "social_facebook",
            "theme": "Infraestrutura",
            "text": "Buracos na rua principal precisam de reparo urgente",
            "sentiment": "NEGATIVO",
            "location": "Timon",
            "timestamp_utc": datetime.utcnow() - timedelta(days=3),
            "url": "https://facebook.com"
        },
        {
            "source_platform": "google_reviews",
            "theme": "Educação",
            "text": "Escola pública com ótima infraestrutura",
            "sentiment": "POSITIVO",
            "location": "Codó",
            "timestamp_utc": datetime.utcnow() - timedelta(days=5),
            "url": "https://google.com"
        }
    ]
    
    inserted = 0
    for record in test_records:
        try:
            create_mention(db, record)
            inserted += 1
        except Exception as e:
            print(f"  ❌ Erro ao inserir: {e}")
    
    db.commit()
    print(f"✅ {inserted} registros inseridos com sucesso")
    
    # Recontagem
    count = db.query(Mention).count()
    print(f"📊 Total após inserção: {count}")

# 6. Testa o DataAnalyzer
print("\n[6/6] Testando DataAnalyzer...")
try:
    from backend.collectors.data_analyzer import DataAnalyzer
    
    analyzer = DataAnalyzer(db)
    df = analyzer.fetch_all_data()
    
    print(f"📊 DataFrame carregado com {len(df)} linhas")
    
    if not df.empty:
        print("\n✅ Colunas do DataFrame:")
        for col in df.columns:
            print(f"  - {col}")
        
        print("\n✅ Primeiras linhas:")
        print(df.head(3).to_string())
        
        # Testa análise
        print("\n🔬 Testando análise completa...")
        analysis, df_with_quality = analyzer.analyze_dataset(df)
        
        print("\n📈 Resultado da Análise:")
        print(f"  Total de registros: {analysis.get('total_records', 0)}")
        print(f"  Qualidade média: {analysis.get('quality_metrics', {}).get('average_score', 0)}")
        print(f"  Fontes únicas: {len(analysis.get('by_source', []))}")
        print(f"  Temas únicos: {len(analysis.get('by_theme', []))}")
        
        # Testa tabelas comparativas
        print("\n📊 Testando tabelas comparativas...")
        tables = analyzer.generate_comparison_tables(df_with_quality)
        
        print(f"  Tabelas geradas:")
        for table_name, table_data in tables.items():
            if isinstance(table_data, list):
                print(f"    - {table_name}: {len(table_data)} registros")
            elif isinstance(table_data, dict):
                print(f"    - {table_name}: {len(table_data.get('distribution', []))} categorias")
    else:
        print("⚠️  DataFrame vazio mesmo com dados no banco!")
        print("Verificando a query...")
        
        # Query direta para debug
        mentions = db.query(Mention).all()
        print(f"Query direta retornou: {len(mentions)} registros")
        
        if mentions:
            print("\nPrimeiro registro:")
            m = mentions[0]
            print(f"  ID: {m.id}")
            print(f"  Fonte: {m.source_platform}")
            print(f"  Tema: {m.theme}")
            print(f"  Texto: {m.text}")
            
except Exception as e:
    print(f"❌ Erro no DataAnalyzer: {e}")
    import traceback
    traceback.print_exc()

# Fecha conexão
db.close()

print("\n" + "="*60)
print("✅ DIAGNÓSTICO COMPLETO")
print("="*60)
print("\n🎯 PRÓXIMOS PASSOS:")
print("1. Se houver dados no banco, teste os endpoints:")
print("   http://localhost:8000/api/data/analysis")
print("   http://localhost:8000/api/data/comparison-tables")
print("\n2. Se os endpoints retornarem JSON vazio, reinicie o backend:")
print("   python -m uvicorn backend.main:app --reload")
print("\n3. Abra o frontend:")
print("   Abra templates/fonte_de_dados.html no navegador")
print("="*60)