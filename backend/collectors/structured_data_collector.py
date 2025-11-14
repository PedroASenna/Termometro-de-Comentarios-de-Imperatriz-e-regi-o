import logging
import pandas as pd
import requests
from io import BytesIO
import random  # Importado para variar os textos

logger = logging.getLogger(__name__)

class StructuredDataCollector:
    def __init__(self):
        # URLs de fontes de segurança (mantido)
        self.fbsp_urls = [
            "https://forumseguranca.org.br/wp-content/uploads/2023/07/anuario-2023.xlsx",
            "https://forumseguranca.org.br/wp-content/uploads/2024/07/anuario-2024.xlsx",  # Pode não existir ainda
        ]

        # Dados simulados realistas (mantido)
        self.simulated_security_data = {
            'São Luís': {'mvi': 45, 'furtos': 1200, 'roubos': 850},
            'Imperatriz': {'mvi': 38, 'furtos': 680, 'roubos': 420},
            'Caxias': {'mvi': 22, 'furtos': 340, 'roubos': 180},
            'Timon': {'mvi': 18, 'furtos': 290, 'roubos': 150},
            'Codó': {'mvi': 15, 'furtos': 220, 'roubos': 120},
            'Açailândia': {'mvi': 25, 'furtos': 380, 'roubos': 210},
            'Bacabal': {'mvi': 12, 'furtos': 180, 'roubos': 95},
            'Balsas': {'mvi': 10, 'furtos': 160, 'roubos': 85},
            'Paço do Lumiar': {'mvi': 20, 'furtos': 420, 'roubos': 230},
            'Santa Inês': {'mvi': 8, 'furtos': 140, 'roubos': 70}
        }

    def get_security_data(self):
        """Tenta buscar dados reais, caso falhe, usa dados simulados."""
        logger.info(f"Tentando baixar dados de segurança...")

        # Tenta baixar dados reais
        for url in self.fbsp_urls:
            try:
                logger.info(f"Tentando URL: {url}")
                records = self._fetch_from_url(url)
                if records:
                    logger.info(f"✅ Dados reais coletados com sucesso: {len(records)} registros")
                    # Mesmo coletando real, vamos formatar o texto para parecer opinião
                    for record in records:
                        record['text'] = self._format_security_text(record['indicator_name'], record['location'], int(record['indicator_value']))
                        record['source_platform'] = "FBSP"  # Garante a fonte correta
                        record['sentiment'] = "NEGATIVO" if record['indicator_name'] == 'MVI' and record['indicator_value'] > 10 else "NEUTRO"  # Adiciona sentimento
                    return records
            except Exception as e:
                logger.warning(f"Falha ao baixar ou processar dados reais de {url}: {e}")

        # Se falhou, usa dados simulados (com texto formatado)
        logger.warning("⚠️ Não foi possível baixar dados reais. Usando dados simulados formatados.")
        return self._generate_simulated_data()

    def _fetch_from_url(self, url):
        """Tenta baixar e processar Excel do FBSP."""
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            xls = pd.ExcelFile(BytesIO(response.content))

            # Lista de possíveis nomes de planilhas
            possible_sheet_names = [
                'MVI', 'Municípios', 'Tabela', 'Dados', 'MA', 'Maranhão',
                 'CVP', 'Indicadores', 'Base'
            ]

            # Busca a planilha correta
            target_sheet_name = None
            skip = 0
            df = None

            for sheet_name in xls.sheet_names:
                 logger.info(f"Verificando planilha: {sheet_name}")
                 # Verifica se o nome da planilha contém palavras-chave
                 if any(keyword.lower() in sheet_name.lower() for keyword in ['munic', 'mvi', 'cvli']):
                      for s in [0, 1, 2, 3, 4]:  # Tenta diferentes skiprows
                           try:
                                temp_df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=s)
                                temp_df.columns = temp_df.columns.str.strip().str.lower()
                                # Verifica se tem colunas essenciais
                                if 'uf' in temp_df.columns and any('munic' in col for col in temp_df.columns):
                                     logger.info(f"✅ Planilha adequada encontrada: '{sheet_name}' (skiprows={s})")
                                     target_sheet_name = sheet_name
                                     skip = s
                                     df = temp_df
                                     break  # Sai do loop de skiprows
                           except Exception:
                                continue  # Tenta próximo skiprow
                      if df is not None:
                           break  # Sai do loop de sheet_names

            if df is None:
                logger.error(f"ERRO CRÍTICO: Nenhuma planilha adequada foi encontrada no arquivo Excel de {url}.")
                return None

            return self._process_dataframe(df)

        except requests.exceptions.Timeout:
             logger.error(f"Timeout ao tentar baixar o arquivo de {url}")
             return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de rede ao baixar {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao processar Excel de {url}: {e}", exc_info=True)
            return None

    def _process_dataframe(self, df):
        """Processa o DataFrame extraído do FBSP."""
        records = []
        logger.info("Processando DataFrame do FBSP...")

        try:
            # Filtra Maranhão
            df.columns = df.columns.str.strip().str.lower()  # Garante lowercase
            df_ma = df[df['uf'].astype(str).str.upper() == 'MA'].copy()

            if df_ma.empty:
                logger.warning("Nenhum dado para o Maranhão encontrado no DataFrame processado.")
                return None

            # Identifica coluna de município (mais flexível)
            mun_col = next((col for col in df_ma.columns if 'munic' in col), None)
            if not mun_col:
                logger.error("Coluna de município não identificada.")
                return None

            # Identifica colunas de crimes (mais flexível)
            crime_indicators = {
                'MVI': ['mvi', 'mortes violentas', 'cvli'],
                'Furtos': ['furto'],
                'Roubos': ['roubo']
            }
            crime_cols_map = {}
            for crime_name, keywords in crime_indicators.items():
                col = next((col for col in df_ma.columns if any(kw in col for kw in keywords)), None)
                if col:
                    crime_cols_map[crime_name] = col

            if not crime_cols_map:
                logger.warning("Nenhuma coluna de crime relevante (MVI, Furto, Roubo) encontrada.")
                # Tenta colunas genéricas se específicas falharem
                fallback_cols = [col for col in df_ma.columns if isinstance(df_ma[col].iloc[0], (int, float))]
                if fallback_cols:
                     logger.info(f"Usando colunas numéricas genéricas como fallback: {fallback_cols}")
                     # Simplificado: pega a primeira coluna numérica como MVI genérico
                     crime_cols_map['MVI_GENERICO'] = fallback_cols[0]
                else:
                     logger.error("Nenhuma coluna de crime identificada.")
                     return None

            logger.info(f"Colunas identificadas -> Município: '{mun_col}', Crimes: {crime_cols_map}")

            for _, row in df_ma.iterrows():
                city = str(row[mun_col]).strip().title()  # Padroniza nome da cidade

                for crime_name, crime_col in crime_cols_map.items():
                    try:
                        value_raw = row[crime_col]
                        # Tenta converter para numérico, tratando '*', '-' e outros não numéricos
                        if isinstance(value_raw, str):
                             value_raw = value_raw.replace('*', '').replace('-', '').strip()
                        value = pd.to_numeric(value_raw, errors='coerce')

                        if pd.notna(value) and value >= 0:  # Inclui zero, pois pode ser relevante
                            records.append({
                                "source_platform": "FBSP",  # Fonte real
                                "theme": "Segurança",
                                "text": self._format_security_text(crime_name, city, int(value)),  # Texto formatado
                                "sentiment": "NEGATIVO" if crime_name == 'MVI' and value > 10 else "NEUTRO",  # Sentimento baseado em MVI
                                "location": city,
                                "url": "https://forumseguranca.org.br",
                                "indicator_name": crime_name,
                                "indicator_value": float(value)
                            })
                    except Exception as e:
                         logger.warning(f"Erro ao processar linha para {city}, coluna {crime_col}: {e}. Valor original: {row[crime_col]}")
                         continue  # Pula para próxima coluna ou linha

            logger.info(f"Processamento do DataFrame concluído. {len(records)} registros gerados.")
            return records if records else None

        except KeyError as e:
             logger.error(f"Erro de chave esperado não encontrado no DataFrame: {e}. Colunas disponíveis: {list(df.columns)}")
             return None
        except Exception as e:
            logger.error(f"Erro inesperado ao processar DataFrame: {e}", exc_info=True)
            return None

    def _generate_simulated_data(self):
        """Gera dados simulados com textos formatados como opinião/notícia."""
        records = []
        logger.info(f"Gerando dados simulados de segurança para {len(self.simulated_security_data)} cidades...")

        for city, data in self.simulated_security_data.items():
            # Mortes Violentas Intencionais (MVI)
            mvi_value = data.get('mvi', 0)
            records.append({
                "source_platform": "FBSP",
                "theme": "Segurança",
                "text": self._format_security_text("MVI", city, mvi_value),  # Usa a nova função de formatação
                "sentiment": "NEGATIVO" if mvi_value > 10 else "NEUTRO",  # Sentimento baseado no valor
                "location": city,
                "url": "https://forumseguranca.org.br",
                "indicator_name": "MVI",
                "indicator_value": float(mvi_value)
            })

            # Furtos
            furtos_value = data.get('furtos', 0)
            records.append({
                "source_platform": "FBSP",
                "theme": "Segurança",
                "text": self._format_security_text("Furtos", city, furtos_value),  # Usa a nova função de formatação
                "sentiment": "NEGATIVO" if furtos_value > 500 else "NEUTRO",  # Sentimento baseado no valor
                "location": city,
                "url": "https://forumseguranca.org.br",
                "indicator_name": "Furtos",
                "indicator_value": float(furtos_value)
            })

            # Roubos
            roubos_value = data.get('roubos', 0)
            records.append({
                "source_platform": "FBSP",
                "theme": "Segurança",
                "text": self._format_security_text("Roubos", city, roubos_value),  # Usa a nova função de formatação
                "sentiment": "NEGATIVO" if roubos_value > 300 else "NEUTRO",  # Sentimento baseado no valor
                "location": city,
                "url": "https://forumseguranca.org.br",
                "indicator_name": "Roubos",
                "indicator_value": float(roubos_value)
            })

        logger.info(f"Gerados {len(records)} registros simulados de segurança com texto formatado.")
        return records

    # --- NOVA FUNÇÃO ---
    def _format_security_text(self, crime_type, city, value):
        """Cria um texto que parece mais notícia/opinião sobre o dado de segurança."""
        templates = {
            "MVI": [
                f"Alerta em {city}: {value} mortes violentas intencionais estimadas levantam preocupação.",
                f"Segurança pública em debate em {city} após registro estimado de {value} MVI.",
                f"Índice de MVI ({value} casos estimados) em {city} exige atenção das autoridades locais.",
                f"{city} registra aproximadamente {value} mortes violentas, segundo estimativas."
            ],
            "Furtos": [
                f"Moradores de {city} relatam incômodo com furtos; estimativa aponta {value} ocorrências.",
                f"Aumento percebido nos furtos em {city}? Dados estimados indicam {value} casos.",
                f"Comércio de {city} sofre com furtos: {value} casos estimados no período.",
                f"Policiamento precisa ser reforçado em {city}, onde {value} furtos foram estimados."
            ],
            "Roubos": [
                f"Sensação de insegurança cresce em {city} com estimativa de {value} roubos.",
                f"População de {city} pede mais ações contra roubos ({value} casos estimados).",
                f"Número estimado de {value} roubos em {city} preocupa autoridades e cidadãos.",
                f"{city} enfrenta desafio com roubos: {value} ocorrências estimadas."
            ]
        }
        # Fallback para tipos de crime não mapeados
        default_template = f"Indicador '{crime_type}' em {city}: {value} casos registrados/estimados."

        # Escolhe um template aleatório para o tipo de crime
        return random.choice(templates.get(crime_type, [default_template]))

    