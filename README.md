# Termômetro do Maranhão

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
