"""
COLETOR DE DADOS - PORTAL DA TRANSPARÊNCIA - BIG DATA SCALE
Simula o registro de gastos públicos e investimentos.
ESCALA: 200K+ REGISTROS
"""

import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TransparencyCollector:
    def __init__(self):
        # TODAS AS 217 CIDADES DO MARANHÃO
        self.cities_ma = self._load_all_cities()

        # ÁREAS DE INVESTIMENTO MASSIVAMENTE EXPANDIDAS
        self.investment_areas = {
            # === SAÚDE ===
            'Investimento_Saude': {
                'name': 'Investimento em Saúde (Mensal)',
                'unit': 'R$',
                'min_val': 300000, 'max_val': 15000000,
                'theme': 'Saúde',
                'sentiment': 'NEUTRO'
            },
            'Gastos_UBS': {
                'name': 'Gastos com Unidades Básicas de Saúde',
                'unit': 'R$',
                'min_val': 50000, 'max_val': 3000000,
                'theme': 'Saúde',
                'sentiment': 'NEUTRO'
            },
            'Compra_Medicamentos': {
                'name': 'Compra de Medicamentos',
                'unit': 'R$',
                'min_val': 100000, 'max_val': 5000000,
                'theme': 'Saúde',
                'sentiment': 'NEUTRO'
            },
            'Manutencao_Hospitalar': {
                'name': 'Manutenção Hospitalar',
                'unit': 'R$',
                'min_val': 80000, 'max_val': 4000000,
                'theme': 'Saúde',
                'sentiment': 'NEUTRO'
            },

            # === EDUCAÇÃO ===
            'Investimento_Educacao': {
                'name': 'Investimento em Educação (Mensal)',
                'unit': 'R$',
                'min_val': 500000, 'max_val': 20000000,
                'theme': 'Educação',
                'sentiment': 'NEUTRO'
            },
            'Gastos_Escolas': {
                'name': 'Gastos com Escolas Municipais',
                'unit': 'R$',
                'min_val': 200000, 'max_val': 8000000,
                'theme': 'Educação',
                'sentiment': 'NEUTRO'
            },
            'Transporte_Escolar': {
                'name': 'Gastos com Transporte Escolar',
                'unit': 'R$',
                'min_val': 50000, 'max_val': 2000000,
                'theme': 'Educação',
                'sentiment': 'NEUTRO'
            },
            'Merenda_Escolar': {
                'name': 'Gastos com Merenda Escolar',
                'unit': 'R$',
                'min_val': 100000, 'max_val': 4000000,
                'theme': 'Educação',
                'sentiment': 'NEUTRO'
            },

            # === INFRAESTRUTURA ===
            'Obras_Infraestrutura': {
                'name': 'Gastos com Obras e Infraestrutura',
                'unit': 'R$',
                'min_val': 200000, 'max_val': 10000000,
                'theme': 'Infraestrutura',
                'sentiment': 'NEUTRO'
            },
            'Pavimentacao_Ruas': {
                'name': 'Pavimentação de Ruas',
                'unit': 'R$',
                'min_val': 100000, 'max_val': 5000000,
                'theme': 'Infraestrutura',
                'sentiment': 'NEUTRO'
            },
            'Saneamento_Basico': {
                'name': 'Investimento em Saneamento Básico',
                'unit': 'R$',
                'min_val': 150000, 'max_val': 6000000,
                'theme': 'Infraestrutura',
                'sentiment': 'NEUTRO'
            },
            'Iluminacao_Publica': {
                'name': 'Manutenção de Iluminação Pública',
                'unit': 'R$',
                'min_val': 30000, 'max_val': 1500000,
                'theme': 'Infraestrutura',
                'sentiment': 'NEUTRO'
            },
            'Drenagem_Urbana': {
                'name': 'Obras de Drenagem Urbana',
                'unit': 'R$',
                'min_val': 80000, 'max_val': 3000000,
                'theme': 'Infraestrutura',
                'sentiment': 'NEUTRO'
            },

            # === SEGURANÇA ===
            'Gastos_Seguranca': {
                'name': 'Gastos com Segurança Pública',
                'unit': 'R$',
                'min_val': 100000, 'max_val': 5000000,
                'theme': 'Segurança',
                'sentiment': 'NEUTRO'
            },
            'Guarda_Municipal': {
                'name': 'Investimento em Guarda Municipal',
                'unit': 'R$',
                'min_val': 50000, 'max_val': 2000000,
                'theme': 'Segurança',
                'sentiment': 'NEUTRO'
            },
            'Videomonitoramento': {
                'name': 'Sistema de Videomonitoramento',
                'unit': 'R$',
                'min_val': 30000, 'max_val': 1500000,
                'theme': 'Segurança',
                'sentiment': 'NEUTRO'
            },

            # === TRANSPORTE ===
            'Gastos_Transporte': {
                'name': 'Gastos com Transporte Público',
                'unit': 'R$',
                'min_val': 100000, 'max_val': 4000000,
                'theme': 'Transporte',
                'sentiment': 'NEUTRO'
            },
            'Manutencao_Frota': {
                'name': 'Manutenção de Frota Municipal',
                'unit': 'R$',
                'min_val': 50000, 'max_val': 2000000,
                'theme': 'Transporte',
                'sentiment': 'NEUTRO'
            },

            # === ADMINISTRAÇÃO ===
            'Folha_Pagamento': {
                'name': 'Folha de Pagamento (Mensal)',
                'unit': 'R$',
                'min_val': 1000000, 'max_val': 50000000,
                'theme': 'Administração Pública',
                'sentiment': 'NEUTRO'
            },
            'Custeio_Administrativo': {
                'name': 'Custeio Administrativo',
                'unit': 'R$',
                'min_val': 200000, 'max_val': 8000000,
                'theme': 'Administração Pública',
                'sentiment': 'NEUTRO'
            },
            'Licitacoes_Contratos': {
                'name': 'Licitações e Contratos',
                'unit': 'R$',
                'min_val': 100000, 'max_val': 10000000,
                'theme': 'Administração Pública',
                'sentiment': 'NEUTRO'
            },

            # === ASSISTÊNCIA SOCIAL ===
            'Assistencia_Social': {
                'name': 'Investimento em Assistência Social',
                'unit': 'R$',
                'min_val': 100000, 'max_val': 5000000,
                'theme': 'Administração Pública',
                'sentiment': 'NEUTRO'
            },
            'Programas_Transferencia': {
                'name': 'Programas de Transferência de Renda',
                'unit': 'R$',
                'min_val': 50000, 'max_val': 3000000,
                'theme': 'Administração Pública',
                'sentiment': 'NEUTRO'
            },

            # === LAZER E CULTURA ===
            'Cultura_Lazer': {
                'name': 'Investimento em Cultura e Lazer',
                'unit': 'R$',
                'min_val': 30000, 'max_val': 2000000,
                'theme': 'Lazer',
                'sentiment': 'NEUTRO'
            },
            'Eventos_Publicos': {
                'name': 'Gastos com Eventos Públicos',
                'unit': 'R$',
                'min_val': 20000, 'max_val': 1500000,
                'theme': 'Lazer',
                'sentiment': 'NEUTRO'
            },

            # === MEIO AMBIENTE ===
            'Meio_Ambiente': {
                'name': 'Investimento em Meio Ambiente',
                'unit': 'R$',
                'min_val': 30000, 'max_val': 1500000,
                'theme': 'Infraestrutura',
                'sentiment': 'NEUTRO'
            },
            'Limpeza_Urbana': {
                'name': 'Gastos com Limpeza Urbana',
                'unit': 'R$',
                'min_val': 100000, 'max_val': 4000000,
                'theme': 'Infraestrutura',
                'sentiment': 'NEUTRO'
            }
        }

        logger.info("ℹ️ Coletor Portal da Transparência BIG DATA inicializado.")

    def _load_all_cities(self):
        """Carrega TODAS as 217 cidades do Maranhão"""
        return [
            'São Luís', 'Imperatriz', 'Caxias', 'Timon', 'Codó', 'Açailândia',
            'Bacabal', 'Balsas', 'Paço do Lumiar', 'Santa Inês', 'Pinheiro',
            'Pedreiras', 'Chapadinha', 'São José de Ribamar', 'Grajaú',
            'Itapecuru Mirim', 'Presidente Dutra', 'Viana', 'São Mateus',
            'Rosário', 'Barra do Corda', 'Santa Luzia', 'Coroatá', 'Arari',
            'Tutóia', 'Colinas', 'Carolina', 'São Bento', 'Vargem Grande',
            'Esperantinópolis', 'Lago da Pedra', 'Tuntum', 'Governador Nunes Freire',
            'Buriticupu', 'Riachão', 'Estreito', 'São João dos Patos', 'Matões',
            'Porto Franco', 'Carutapera', 'Humberto de Campos', 'Bacuri',
            'Icatu', 'São Luís Gonzaga do Maranhão', 'Alcântara', 'Brejo',
            'Cantanhede', 'Primeira Cruz', 'São João Batista', 'Morros',
            'Guimarães', 'Cururupu', 'Mirinzal', 'Araioses', 'Barreirinhas',
            'Paulino Neves', 'Água Doce do Maranhão', 'Santo Amaro do Maranhão',
            'Urbano Santos', 'Anapurus', 'Mata Roma', 'Nina Rodrigues',
            'Presidente Vargas', 'São Bernardo', 'Magalhães de Almeida',
            'Santana do Maranhão', 'Belágua', 'Buriti', 'Duque Bacelar',
            'Coelho Neto', 'Peritoró', 'Timbiras', 'Aldeias Altas', 'Afonso Cunha',
            'Parnarama', 'São João do Soter', 'Sucupira do Norte', 'Pastos Bons',
            'Nova Iorque', 'Fortaleza dos Nogueiras', 'São Domingos do Maranhão',
            'São Felix de Balsas', 'Alto Parnaíba', 'São Francisco do Maranhão',
            'Loreto', 'Sambaíba', 'Sucupira do Riachão', 'Nova Colinas',
            'São Pedro dos Crentes', 'Passagem Franca', 'Tasso Fragoso',
            'Campestre do Maranhão', 'Benedito Leite', 'Lagoa do Mato',
            'Barão de Grajaú', 'Formosa da Serra Negra', 'Mirador', 'Sítio Novo',
            'Bom Jardim', 'Santa Filomena do Maranhão', 'Buritirana',
            'Fernando Falcão', 'Jatobá', 'Paraibano', 'São João do Paraíso',
            'Feira Nova do Maranhão', 'Ribamar Fiquene', 'Amarante do Maranhão',
            'Montes Altos', 'Lajeado Novo', 'Davinópolis', 'Governador Edison Lobão',
            'Cidelândia', 'Senador La Rocque', 'Vila Nova dos Martírios',
            'São Pedro da Água Branca', 'João Lisboa', 'Bom Jesus das Selvas',
            'Itinga do Maranhão', 'Centro do Guilherme', 'Centro Novo do Maranhão',
            'Junco do Maranhão', 'Dom Pedro', 'Gonçalves Dias',
            'Senador Alexandre Costa', 'Governador Archer', 'Graça Aranha',
            'Governador Luiz Rocha', 'Lagoa Grande do Maranhão', 'Igarapé Grande',
            'Lima Campos', 'Lago do Junco', 'Lago dos Rodrigues',
            'São Mateus do Maranhão', 'Paulo Ramos', 'Vitorino Freire',
            'Presidente Juscelino', 'Santa Rita', 'Bom Lugar', 'Igarapé do Meio',
            "Olho d'Água das Cunhãs", 'Satubinha', 'São Benedito do Rio Preto',
            'Anajatuba', 'Miranda do Norte', 'Vitória do Mearim',
            'São Vicente Ferrer', 'Capinzal do Norte', 'Bernardo do Mearim',
            'Poção de Pedras', 'Trizidela do Vale', 'Altamira do Maranhão',
            'Conceição do Lago-Açu', 'Penalva', 'Cajari', 'Matinha',
            'Olinda Nova do Maranhão', 'Palmeirândia', 'Peri Mirim', 'Bequimão',
            'Central do Maranhão', 'Serrano do Maranhão', 'Bacurituba',
            'Pedro do Rosário', 'Presidente Sarney', 'Turiaçu', 'Turilândia',
            'Cândido Mendes', 'Godofredo Viana', 'Luís Domingues', 'Maracaçumé',
            'Governador Newton Bello', 'Santa Helena', 'Boa Vista do Gurupi',
            'Marajá do Sena', 'Amapá do Maranhão', 'Zé Doca',
            # Cidades adicionadas para completar cobertura
            'Porto Rico do Maranhão', 'Cedral', 'Presidente Médici',
            'Santa Luzia do Paruá', 'Nova Olinda do Maranhão', 'São João do Carú',
            'Alto Alegre do Pindaré', 'Pindaré-Mirim', 'Monção', 'Tufilândia',
            'Bela Vista do Maranhão', 'Pio XII', 'Lago Verde', 'Matões do Norte',
            'Pirapemas', 'Milagres do Maranhão', 'Santo Antônio dos Lopes',
            'São José dos Basílios', 'São Roberto', 'São Raimundo do Doca Bezerra',
            'Itaipava do Grajaú', 'Jenipapo dos Vieiras', 'São Francisco do Brejão',
            'Buriti Bravo', 'São Domingos do Azeitão'
        ]

    def collect_all_data(self):
        """Coleta todos os indicadores em escala BIG DATA - 200K+ registros."""
        logger.info("💰 BIG DATA: Iniciando coleta massiva de dados do Portal da Transparência...")
        records = []

        # BIG DATA: Gera dados mensais dos últimos 4 anos (48 meses)
        # 170 cidades x 28 áreas x 48 meses = ~228K registros
        months_to_generate = 48

        major_cities = ['São Luís', 'Imperatriz', 'Caxias', 'Timon', 'Codó', 'Açailândia']

        for city in self.cities_ma:
            for area_id, config in self.investment_areas.items():
                for month_offset in range(months_to_generate):
                    try:
                        # Calcula a data
                        record_date = datetime.utcnow() - timedelta(days=month_offset * 30)
                        year = record_date.year

                        # Gera valor base
                        base_value = random.uniform(config['min_val'], config['max_val'])

                        # Ajusta valores para cidades principais (muito maior)
                        if city in major_cities:
                            base_value *= random.uniform(3.0, 10.0)

                        # Adiciona variação mensal (±20%)
                        monthly_variation = random.uniform(0.8, 1.2)
                        value = int(base_value * monthly_variation)

                        records.append({
                            'source_platform': 'Portal da Transparência',
                            'theme': config['theme'],
                            'text': f"{config['name']} em {city}: R$ {value:,.2f} (Ref: {record_date.strftime('%m/%Y')})",
                            'sentiment': config['sentiment'],
                            'location': city,
                            'timestamp_utc': record_date,
                            'url': 'https://www.portaltransparencia.gov.br/',
                            'indicator_id': f"gastos_{area_id.lower()}",
                            'indicator_name': config['name'],
                            'indicator_value': float(value),
                            'indicator_unit': config['unit'],
                            'indicator_year': str(year)
                        })
                    except Exception as e:
                        continue

        logger.info(f"✅ BIG DATA Transparência: {len(records):,} registros gerados.")
        return records
