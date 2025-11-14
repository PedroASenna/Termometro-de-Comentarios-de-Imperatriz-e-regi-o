"""
SCRIPT DE DIAGNÓSTICO - Verifica sentimentos no banco
"""

import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from backend.database import SessionLocal
from backend.models import Mention
from sqlalchemy import func

def check_sentiments():
    db = SessionLocal()
    
    print("\n" + "="*70)
    print("🔍 DIAGNÓSTICO DE SENTIMENTOS - TERMÔMETRO DO MARANHÃO")
    print("="*70)
    
    # Total de registros
    total = db.query(Mention).count()
    print(f"\n📊 Total de registros: {total}")
    
    # Por sentimento (todos os valores)
    print("\n📈 Contagem por SENTIMENTO (valores exatos):")
    sentiments = db.query(
        Mention.sentiment,
        func.count(Mention.id)
    ).group_by(Mention.sentiment).all()
    
    for sentiment, count in sentiments:
        percentage = (count / total * 100) if total > 0 else 0
        print(f"   '{sentiment}': {count} ({percentage:.1f}%)")
    
    # Por fonte
    print("\n📡 Contagem por FONTE:")
    sources = db.query(
        Mention.source_platform,
        func.count(Mention.id)
    ).group_by(Mention.source_platform).all()
    
    for source, count in sources:
        print(f"   {source}: {count}")
    
    # Por tema
    print("\n🏷️  Contagem por TEMA:")
    themes = db.query(
        Mention.theme,
        func.count(Mention.id)
    ).group_by(Mention.theme).all()
    
    for theme, count in themes:
        print(f"   {theme}: {count}")
    
    # Google Maps específico
    print("\n🗺️  GOOGLE MAPS - Detalhes:")
    gmaps = db.query(Mention).filter(
        Mention.source_platform == 'Google Maps'
    ).all()
    
    if gmaps:
        print(f"   Total Google Maps: {len(gmaps)}")
        
        gmaps_sentiments = {}
        for record in gmaps:
            sent = record.sentiment or 'NULL'
            gmaps_sentiments[sent] = gmaps_sentiments.get(sent, 0) + 1
        
        print("   Sentimentos:")
        for sent, count in gmaps_sentiments.items():
            print(f"      '{sent}': {count}")
        
        # Mostra exemplos
        print("\n   📝 Exemplos de registros Google Maps:")
        for i, record in enumerate(gmaps[:3], 1):
            print(f"\n   {i}. Sentimento: '{record.sentiment}'")
            print(f"      Tema: {record.theme}")
            print(f"      Texto: {record.text[:80]}...")
    else:
        print("   ⚠️ Nenhum registro do Google Maps encontrado!")
    
    # Verifica COMÉRCIO especificamente
    print("\n🛒 TEMA COMÉRCIO - Detalhes:")
    comercio = db.query(Mention).filter(
        Mention.theme == 'Comércio'
    ).all()
    
    if comercio:
        print(f"   Total Comércio: {len(comercio)}")
        
        comercio_sentiments = {}
        for record in comercio:
            sent = record.sentiment or 'NULL'
            comercio_sentiments[sent] = comercio_sentiments.get(sent, 0) + 1
        
        print("   Sentimentos:")
        for sent, count in comercio_sentiments.items():
            percentage = (count / len(comercio) * 100) if len(comercio) > 0 else 0
            print(f"      '{sent}': {count} ({percentage:.1f}%)")
        
        # Calcula satisfação
        positivo = comercio_sentiments.get('POSITIVO', 0) + comercio_sentiments.get('POSITIVE', 0)
        negativo = comercio_sentiments.get('NEGATIVO', 0) + comercio_sentiments.get('NEGATIVE', 0)
        
        satisfacao = (positivo / len(comercio) * 100) if len(comercio) > 0 else 0
        print(f"\n   📊 Cálculo de Satisfação COMÉRCIO:")
        print(f"      Positivas: {positivo}")
        print(f"      Negativas: {negativo}")
        print(f"      Total: {len(comercio)}")
        print(f"      Satisfação: {satisfacao:.1f}%")
    
    # Verifica valores problemáticos
    print("\n⚠️  PROBLEMAS DETECTADOS:")
    
    # Sentimentos vazios ou null
    null_sent = db.query(Mention).filter(
        (Mention.sentiment == None) | (Mention.sentiment == '')
    ).count()
    
    if null_sent > 0:
        print(f"   ⚠️ {null_sent} registros com sentimento NULL/vazio")
    
    # Sentimentos em inglês
    english_sent = db.query(Mention).filter(
        Mention.sentiment.in_(['POSITIVE', 'NEGATIVE', 'NEUTRAL'])
    ).count()
    
    if english_sent > 0:
        print(f"   ⚠️ {english_sent} registros com sentimento em INGLÊS")
        print(f"      Execute: UPDATE mentions SET sentiment = CASE")
        print(f"                 WHEN sentiment = 'POSITIVE' THEN 'POSITIVO'")
        print(f"                 WHEN sentiment = 'NEGATIVE' THEN 'NEGATIVO'")
        print(f"                 WHEN sentiment = 'NEUTRAL' THEN 'NEUTRO' END;")
    
    if null_sent == 0 and english_sent == 0:
        print("   ✅ Nenhum problema detectado!")
    
    print("\n" + "="*70)
    db.close()

if __name__ == "__main__":
    check_sentiments()