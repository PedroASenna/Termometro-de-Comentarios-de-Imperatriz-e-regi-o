import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import json
import glob
import os

st.set_page_config(page_title="Termômetro do Maranhão", layout="wide")

@st.cache_data(ttl=300)
def load_all_data():
    jsonl_files = glob.glob('*.jsonl')
    if not jsonl_files: return None, None
    
    all_dfs = [pd.read_json(file, lines=True) for file in jsonl_files]
    df = pd.concat(all_dfs, ignore_index=True)
    df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
    
    # Separa dados estatísticos de dados de menções/notícias
    df_stats = df[df['item_type'] == 'statistic_record'].copy()
    df_mentions = df[df['item_type'] != 'statistic_record'].copy()
    
    return df_stats, df_mentions

@st.cache_data
def load_geojson():
    if not os.path.exists('ma_cities.geojson'): return None
    with open('ma_cities.geojson', 'r', encoding='utf-8') as f:
        return json.load(f)

# --- Carregamento de Dados ---
geojson_data = load_geojson()
df_stats, df_mentions = load_all_data()

st.title("🌡️ Termômetro do Maranhão")
st.markdown("Análise interativa de Segurança, Comércio e Infraestrutura no estado.")

if (df_stats is None and df_mentions is None) or geojson_data is None:
    st.error("Dados não encontrados. Execute `python -m src.main` e verifique se o arquivo `ma_cities.geojson` existe.")
else:
    tab1, tab2, tab3 = st.tabs(["📊 Segurança Pública", "🛒 Comércio", "🏗️ Infraestrutura"])

    with tab1:
        st.header("Indicadores de Segurança Pública")
        df_security_stats = df_stats[df_stats['theme'] == 'Segurança']
        df_security_mentions = df_mentions[df_mentions['theme'] == 'Segurança']

        if not df_security_stats.empty:
            # Extrai o valor do metadado para o mapa
            df_security_stats['homicide_rate'] = df_security_stats['metadata'].apply(lambda x: x.get('value', 0))
            
            fig_map = px.choropleth_mapbox(
                df_security_stats,
                geojson=geojson_data, locations='location', featureidkey="properties.name",
                color='homicide_rate', color_continuous_scale="Reds",
                mapbox_style="carto-positron", zoom=5.5, center={"lat": -5.5, "lon": -45.5},
                labels={'homicide_rate': 'Homicídios Dolosos'}
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Nenhum dado estatístico de segurança encontrado para exibir no mapa.")

        st.subheader("Notícias Recentes sobre Segurança")
        for _, row in df_security_mentions.sort_values(by='timestamp_utc', ascending=False).head(5).iterrows():
            st.markdown(f"**Fonte:** {row['source_platform']} | **Sentimento:** {row['sentimento']}")
            st.markdown(f"> {row['text']}")
            if 'url' in row.get('metadata', {}):
                st.markdown(f"[Ler notícia completa]({row['metadata']['url']})")
            st.markdown("---")

    with tab2:
        st.header("Indicadores de Comércio e Preços")
        df_commerce_mentions = df_mentions[df_mentions['theme'] == 'Comércio']
        st.info("Coletor de dados estatísticos de comércio (ex: Cesta Básica) ainda a ser implementado.")
        
        st.subheader("Notícias Recentes sobre Comércio")
        for _, row in df_commerce_mentions.sort_values(by='timestamp_utc', ascending=False).head(5).iterrows():
            st.markdown(f"**Fonte:** {row['source_platform']} | **Sentimento:** {row['sentimento']}")
            st.markdown(f"> {row['text']}")
            if 'url' in row.get('metadata', {}):
                st.markdown(f"[Ler notícia completa]({row['metadata']['url']})")
            st.markdown("---")

    with tab3:
        st.header("Indicadores de Infraestrutura")
        df_infra_mentions = df_mentions[df_mentions['theme'] == 'Infraestrutura']
        st.info("Coletor de dados estatísticos de infraestrutura (ex: Saneamento) ainda a ser implementado.")

        st.subheader("Notícias Recentes sobre Infraestrutura")
        for _, row in df_infra_mentions.sort_values(by='timestamp_utc', ascending=False).head(5).iterrows():
            st.markdown(f"**Fonte:** {row['source_platform']} | **Sentimento:** {row['sentimento']}")
            st.markdown(f"> {row['text']}")
            if 'url' in row.get('metadata', {}):
                st.markdown(f"[Ler notícia completa]({row['metadata']['url']})")
            st.markdown("---")