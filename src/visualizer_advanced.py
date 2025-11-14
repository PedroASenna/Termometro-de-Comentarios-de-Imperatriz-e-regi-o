"""
Visualizador avançado com gráficos interativos e profissionais
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import os
from pathlib import Path
from src.config import DATA_PATHS
import logging
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

class AdvancedVisualizer:
    def __init__(self):
        self.results_path = DATA_PATHS['results']
        Path(self.results_path).mkdir(parents=True, exist_ok=True)
        
        # Cores para temas
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'accent': '#F18F01',
            'success': '#4CAF50',
            'danger': '#F44336',
            'warning': '#FFC107',
            'info': '#17A2B8',
            'dark': '#343A40',
            'light': '#F8F9FA'
        }
        
        # Paleta de cores para sentimentos
        self.sentiment_colors = {
            'POSITIVO': self.colors['success'],
            'NEGATIVO': self.colors['danger'],
            'NEUTRO': self.colors['warning'],
            'LABEL_1': self.colors['success'],
            'LABEL_0': self.colors['danger']
        }

    def generate_interactive_dashboard(self, df, html_filename='dashboard_interativo.html', img_filename='dashboard_profissional.png'):
        """
        Gera um dashboard interativo e profissional
        """
        if df.empty:
            logger.error("DataFrame vazio. Não é possível gerar visualizações.")
            return None

        logger.info(f"Gerando dashboard interativo para {html_filename}...")
        
        # Verificar se a coluna de sentimento existe
        has_sentiment = 'sentimento' in df.columns
        category = df['categoria'].iloc[0] if 'categoria' in df.columns else 'Geral'
        
        # Criar subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Distribuição de Sentimentos',
                'Evolução Temporal dos Sentimentos',
                'Top Hashtags',
                'Engajamento por Sentimento',
                'Nuvem de Palavras - Positivo',
                'Nuvem de Palavras - Negativo'
            ),
            specs=[
                [{"type": "pie"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "image"}, {"type": "image"}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )

        # Personalizar layout geral
        fig.update_layout(
            title_text=f"<b>Análise de Sentimentos - {category}</b>",
            title_font_size=24,
            title_x=0.5,
            title_xanchor="center",
            showlegend=True,
            template="plotly_white",
            height=1200,
            width=1400,
            font=dict(family="Arial, sans-serif", size=12, color="#333"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        # 1. Gráfico de distribuição de sentimentos
        if has_sentiment:
            sentiment_counts = df['sentimento'].value_counts()
            fig.add_trace(
                go.Pie(
                    labels=sentiment_counts.index,
                    values=sentiment_counts.values,
                    marker=dict(colors=[self.sentiment_colors.get(s, self.colors['primary']) for s in sentiment_counts.index]),
                    hole=0.4,
                    name="Sentimentos"
                ),
                row=1, col=1
            )

            # 2. Evolução temporal dos sentimentos
            df_temp = df.copy()
            df_temp['data'] = pd.to_datetime(df_temp['data_criacao']).dt.date
            sentiment_over_time = df_temp.groupby(['data', 'sentimento']).size().unstack(fill_value=0)
            
            for sentiment in sentiment_over_time.columns:
                fig.add_trace(
                    go.Scatter(
                        x=sentiment_over_time.index,
                        y=sentiment_over_time[sentiment],
                        mode='lines+markers',
                        name=sentiment,
                        line=dict(color=self.sentiment_colors.get(sentiment, self.colors['primary']), width=3),
                        marker=dict(size=8)
                    ),
                    row=1, col=2
                )

            # 3. Engajamento por sentimento
            if all(col in df.columns for col in ['curtidas', 'retweets', 'sentimento']):
                engagement = df.groupby('sentimento')[['curtidas', 'retweets']].mean().reset_index()
                
                fig.add_trace(
                    go.Bar(
                        x=engagement['sentimento'],
                        y=engagement['curtidas'],
                        name='Curtidas',
                        marker_color=self.colors['primary'],
                        text=engagement['curtidas'].round(2),
                        textposition='auto',
                    ),
                    row=2, col=2
                )
                
                fig.add_trace(
                    go.Bar(
                        x=engagement['sentimento'],
                        y=engagement['retweets'],
                        name='Retweets',
                        marker_color=self.colors['secondary'],
                        text=engagement['retweets'].round(2),
                        textposition='auto',
                    ),
                    row=2, col=2
                )

        # 4. Top hashtags
        all_hashtags = [tag.lower() for sublist in df['hashtags'] for tag in sublist]
        if all_hashtags:
            top_hashtags = pd.Series(all_hashtags).value_counts().head(10)
            
            fig.add_trace(
                go.Bar(
                    y=[f'#{tag}' for tag in top_hashtags.index],
                    x=top_hashtags.values,
                    orientation='h',
                    marker_color=self.colors['accent'],
                    text=top_hashtags.values,
                    textposition='auto',
                ),
                row=2, col=1
            )

        # 5. Nuvens de palavras
        if has_sentiment:
            # Nuvem de palavras para sentimentos positivos
            positive_texts = ' '.join(df[df['sentimento'].isin(['POSITIVO', 'LABEL_1'])]['texto_limpo'].fillna(''))
            if positive_texts.strip():
                img_pos = self._create_wordcloud_image(positive_texts, 'Greens')
                fig.add_layout_image(
                    dict(
                        source=img_pos,
                        xref="paper", yref="paper",
                        x=0, y=0,
                        sizex=0.5, sizey=0.3,
                        xanchor="left", yanchor="bottom"
                    )
                )

            # Nuvem de palavras para sentimentos negativos
            negative_texts = ' '.join(df[df['sentimento'].isin(['NEGATIVO', 'LABEL_0'])]['texto_limpo'].fillna(''))
            if negative_texts.strip():
                img_neg = self._create_wordcloud_image(negative_texts, 'Reds')
                fig.add_layout_image(
                    dict(
                        source=img_neg,
                        xref="paper", yref="paper",
                        x=0.5, y=0,
                        sizex=0.5, sizey=0.3,
                        xanchor="left", yanchor="bottom"
                    )
                )

        # Atualizar eixos e layout
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        
        # Salvar dashboard interativo
        html_path = os.path.join(self.results_path, html_filename)
        fig.write_html(html_path)
        logger.info(f"Dashboard interativo salvo em: {html_path}")
        
        # Também salvar como imagem estática
        img_path = os.path.join(self.results_path, img_filename)
        fig.write_image(img_path, width=1400, height=1200, scale=2)
        logger.info(f"Dashboard estático salvo em: {img_path}")
        
        return fig

    def _create_wordcloud_image(self, text, colormap):
        """Cria uma nuvem de palavras e retorna como imagem codificada em base64"""
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            colormap=colormap,
            max_words=100
        ).generate(text)
        
        # Converter para imagem
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        # Salvar em buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        
        # Codificar em base64
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{img_str}"

    def generate_statistical_report(self, df, filename='relatorio_estatistico.html'):
        """Gera um relatório estatístico profissional"""
        if df.empty:
            logger.error("DataFrame vazio. Não é possível gerar relatório.")
            return

        logger.info(f"Gerando relatório estatístico para {filename}...")
        
        category = df['categoria'].iloc[0] if 'categoria' in df.columns else 'Geral'

        # Criar relatório com múltiplas visualizações
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Distribuição do Comprimento dos Textos',
                'Relação Curtidas vs Retweets',
                'Distribuição Temporal (por Hora)',
                'Top Usuários por Engajamento'
            ),
            specs=[
                [{"type": "histogram"}, {"type": "scatter"}],
                [{"type": "histogram"}, {"type": "bar"}]
            ]
        )

        # 1. Distribuição do comprimento dos textos
        if 'comprimento_texto' in df.columns:
            fig.add_trace(
                go.Histogram(
                    x=df['comprimento_texto'],
                    nbinsx=20,
                    marker_color=self.colors['primary'],
                    opacity=0.7,
                    name="Comprimento"
                ),
                row=1, col=1
            )

        # 2. Relação entre curtidas e retweets
        if all(col in df.columns for col in ['curtidas', 'retweets']):
            fig.add_trace(
                go.Scatter(
                    x=df['curtidas'],
                    y=df['retweets'],
                    mode='markers',
                    marker=dict(
                        color=self.colors['secondary'],
                        size=8,
                        opacity=0.6
                    ),
                    name="Curtidas vs Retweets"
                ),
                row=1, col=2
            )

        # 3. Distribuição temporal
        if 'data_criacao' in df.columns:
            df_temp = df.copy()
            df_temp['hora'] = pd.to_datetime(df_temp['data_criacao']).dt.hour
            hourly_counts = df_temp['hora'].value_counts().sort_index()
            
            fig.add_trace(
                go.Bar(
                    x=hourly_counts.index,
                    y=hourly_counts.values,
                    marker_color=self.colors['accent'],
                    name="Por Hora"
                ),
                row=2, col=1
            )

        # 4. Top usuários por engajamento
        if all(col in df.columns for col in ['usuario', 'curtidas']):
            top_users = df.groupby('usuario')['curtidas'].sum().nlargest(10)
            
            fig.add_trace(
                go.Bar(
                    x=top_users.values,
                    y=top_users.index,
                    orientation='h',
                    marker_color=self.colors['info'],
                    name="Top Usuários"
                ),
                row=2, col=2
            )

        # Atualizar layout
        fig.update_layout(
            title_text=f"<b>Relatório Estatístico - {category}</b>",
            title_font_size=20,
            title_x=0.5,
            showlegend=True,
            template="plotly_white",
            height=800,
            font=dict(family="Arial, sans-serif", size=12)
        )

        # Salvar relatório
        report_path = os.path.join(self.results_path, filename)
        fig.write_html(report_path)
        logger.info(f"Relatório estatístico salvo em: {report_path}")

    def save_professional_report(self, df):
        """Salva todos os resultados em um relatório profissional completo"""
        if df.empty:
            logger.error("DataFrame vazio. Não é possível salvar relatório.")
            return

        # Gerar visualizações
        self.generate_interactive_dashboard(df, 'dashboard_geral.html', 'dashboard_geral.png')
        self.generate_statistical_report(df, 'relatorio_estatistico_geral.html')
        
        # Salvar dados processados
        csv_path = os.path.join(self.results_path, 'dados_analisados.csv')
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        # Gerar relatório em texto
        self._generate_text_report(df)
        
        logger.info("Relatório profissional completo gerado com sucesso!")

    def _generate_text_report(self, df):
        """Gera um relatório textual detalhado"""
        report_path = os.path.join(self.results_path, 'relatorio_completo.txt')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("RELATÓRIO COMPLETO - ANÁLISE DE SENTIMENTOS\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"Total de registros analisados: {len(df):,}\n\n")
            
            # Estatísticas básicas
            if 'data_criacao' in df.columns:
                f.write(f"Período analisado: {pd.to_datetime(df['data_criacao']).min().date()} a {pd.to_datetime(df['data_criacao']).max().date()}\n")
            
            if 'usuario' in df.columns:
                f.write(f"Usuários únicos: {df['usuario'].nunique():,}\n")
            
            # Estatísticas de sentimentos por categoria
            if 'sentimento' in df.columns and 'categoria' in df.columns:
                for category in df['categoria'].unique():
                    f.write(f"\n--- DISTRIBUIÇÃO DE SENTIMENTOS: {category.upper()} ---\n")
                    category_df = df[df['categoria'] == category]
                    sentiment_counts = category_df['sentimento'].value_counts()
                    for sentiment, count in sentiment_counts.items():
                        percentage = (count / len(category_df)) * 100
                        f.write(f"  {sentiment}: {count:,} ({percentage:.1f}%)\n")
            
            # Estatísticas de engajamento
            f.write("\nESTATÍSTICAS DE ENGAJAMENTO GERAIS:\n")
            if 'curtidas' in df.columns:
                f.write(f"  Total de curtidas: {df['curtidas'].sum():,}\n")
                f.write(f"  Média de curtidas: {df['curtidas'].mean():.2f}\n")
            
            if 'retweets' in df.columns:
                f.write(f"  Total de retweets: {df['retweets'].sum():,}\n")
                f.write(f"  Média de retweets: {df['retweets'].mean():.2f}\n")
            
            # Hashtags mais populares
            f.write("\nHASHTAGS MAIS POPULARES (GERAL):\n")
            all_hashtags = [tag for sublist in df['hashtags'] for tag in sublist]
            if all_hashtags:
                top_hashtags = pd.Series(all_hashtags).value_counts().head(10)
                for i, (hashtag, count) in enumerate(top_hashtags.items(), 1):
                    f.write(f"  {i}. #{hashtag}: {count:,} ocorrências\n")
            else:
                f.write("  Nenhuma hashtag encontrada\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("FIM DO RELATÓRIO\n")
            f.write("=" * 60 + "\n")
        
        logger.info(f"Relatório textual salvo em: {report_path}")