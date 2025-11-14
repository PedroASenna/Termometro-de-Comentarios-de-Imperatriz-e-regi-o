"""
Configurações e constantes do projeto
"""
import os

# QUERIES DE BUSCA PARA O TWITTER
# Aqui você define os alvos da sua coleta.
# Pode adicionar, remover ou modificar categorias e temas.
QUERIES = {
    'Politica': {
        'Prefeito Assis Ramos': '"Assis Ramos" OR prefeito de imperatriz',
        'Governador Carlos Brandão': '"Carlos Brandão" OR governador do maranhão',
        'Governo Federal': 'Lula OR presidente OR "governo federal"',
        'Eleições': 'eleições OR eleição OR urnas',
        'Prefeitura': '"prefeitura de imperatriz" OR prefeitura'
    },
    'Infraestrutura': {
        'Ruas e Asfalto': 'rua OR avenida OR asfalto OR calçamento OR recapeamento',
        'Saneamento e Drenagem': '"buraco na rua" OR lama OR esgoto OR bueiro OR alagamento',
        'Trânsito e Mobilidade': 'trânsito OR semáforo OR pardal OR multa OR engarrafamento',
        'Iluminação Pública': '"iluminação pública" OR "poste apagado" OR "luz queimada"',
        'Transporte Público': '"transporte público" OR ônibus OR "parada de ônibus"',
    },
    'Serviços Públicos': {
        'Saúde': 'saúde OR UPA OR Socorrão OR hospital OR "posto de saúde"',
        'Segurança': 'segurança OR polícia OR assalto OR roubo OR "guarda municipal"',
        'Educação': 'educação OR escola OR creche OR "merenda escolar"'
    }
}

# Configurações da Coleta
COLLECT_SETTINGS = {
    'max_tweets_por_tema': 100  # Máximo de tweets a buscar para cada tema.
}

# Configurações de Localização (Foco em Imperatriz-MA)
LOCATION_SETTINGS = {
    'latitude': -5.5269,
    'longitude': -47.4783,
    'radius': '40km'  # Raio em quilômetros a partir do centro da cidade.
}

# Configurações do Modelo de Análise de Sentimentos
MODEL_SETTINGS = {
    'model_name': 'neuralmind/bert-base-portuguese-cased',
    'max_length': 512
}

# Caminho para salvar o arquivo de dados final
FINAL_DATA_PATH = os.path.join('data', 'results', 'final_data.csv')