# 🌡️ Termômetro de Comentários - Imperatriz e Região

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Ativo-success.svg)

**Sistema inteligente de análise de sentimentos e monitoramento da satisfação popular em Imperatriz/MA e região**

[Características](#-características) • [Instalação](#-instalação) • [Uso](#-uso) • [Arquitetura](#-arquitetura) • [API](#-api) • [Contribuindo](#-contribuindo)

</div>

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Características](#-características)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Instalação](#-instalação)
  - [Windows](#instalação-no-windows)
  - [Linux/Ubuntu](#instalação-no-linuxubuntu)
  - [macOS](#instalação-no-macos)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Fontes de Dados](#-fontes-de-dados)
- [API](#-api)
- [Frontend](#-frontend)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Análise de Dados](#-análise-de-dados)
- [Performance](#-performance)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## 🎯 Sobre o Projeto

O **Termômetro de Comentários** é uma plataforma de Big Data desenvolvida em Python que coleta, processa e analisa dados de múltiplas fontes para medir a satisfação da população de Imperatriz/MA e região. O sistema utiliza técnicas de web scraping, processamento de linguagem natural (NLP) e análise de sentimentos para transformar dados não estruturados em insights visuais e acionáveis.

### 🎓 Contexto Acadêmico
Este projeto foi desenvolvido como trabalho de conclusão de curso, demonstrando aplicação prática de conceitos de:
- Big Data e análise de dados em larga escala
- Web Scraping ético e responsável
- Processamento de Linguagem Natural (NLP)
- Análise de Sentimentos (Sentiment Analysis)
- Arquitetura de sistemas distribuídos
- APIs RESTful com FastAPI
- Visualização de dados geográficos

---

## ✨ Características

### 🔍 Coleta de Dados
- ✅ **Múltiplas Fontes**: DATASUS, IBGE, Google Maps, Reclame Aqui, INEP, Portal da Transparência, FBSP
- ✅ **Web Scraping Inteligente**: Coletores automatizados com retry logic e rate limiting
- ✅ **Dados em Tempo Real**: Atualização automática e programada
- ✅ **Validação de Qualidade**: Score de qualidade para cada registro (0-100)

### 🧠 Processamento e Análise
- ✅ **Análise de Sentimentos**: Classificação automática (Positivo/Negativo/Neutro)
- ✅ **Categorização Temática**: 8 categorias (Saúde, Segurança, Educação, etc.)
- ✅ **Score de Satisfação**: Cálculo ponderado por múltiplos fatores
- ✅ **Análise Temporal**: Tendências e evolução ao longo do tempo
- ✅ **Geolocalização**: Análise por município e região

### 📊 Visualização
- ✅ **Mapa Interativo**: Visualização geográfica com 217 cidades do Maranhão
- ✅ **Termômetro Visual**: Indicador de satisfação em tempo real
- ✅ **Dashboards Dinâmicos**: Gráficos e tabelas interativas
- ✅ **Filtros Avançados**: Por fonte, tema, localização, período e qualidade
- ✅ **Exportação**: Relatórios em múltiplos formatos

### 🚀 Performance
- ✅ **Otimização SQL**: Queries diretas ao banco de dados (sem pandas em produção)
- ✅ **Paginação**: Carregamento eficiente de grandes volumes
- ✅ **Cache Inteligente**: Redução de chamadas desnecessárias à API
- ✅ **Processamento Assíncrono**: FastAPI com async/await
- ✅ **Fallback Robusto**: Sistema resiliente a falhas de fontes externas

---

## 🛠️ Tecnologias

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

- **Python 3.8+**: Linguagem principal
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para banco de dados
- **SQLite**: Banco de dados (ou PostgreSQL para produção)
- **BeautifulSoup4**: Web scraping
- **Requests**: Cliente HTTP
- **Pandas**: Análise de dados (coleta)
- **NumPy**: Computação numérica
- **python-dotenv**: Gerenciamento de variáveis de ambiente

### Frontend
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=leaflet&logoColor=white)

- **HTML5/CSS3**: Interface moderna e responsiva
- **JavaScript (Vanilla)**: Sem dependências pesadas
- **Leaflet.js**: Mapas interativos
- **Chart.js**: Gráficos e visualizações
- **Font Awesome**: Ícones

### DevOps & Ferramentas
- **Git**: Controle de versão
- **VSCode**: IDE
- **Uvicorn**: Servidor ASGI

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Mapa    │  │Termômetro│  │ Gráficos │  │ Tabelas  │   │
│  │ Leaflet  │  │  Visual  │  │ Chart.js │  │ Filtros  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │          │
└───────┼─────────────┼──────────────┼─────────────┼──────────┘
        │             │              │             │
        └─────────────┴──────────────┴─────────────┘
                           │
                    REST API (FastAPI)
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
   ┌────▼────┐                          ┌────▼────┐
   │  CRUD   │                          │ Analysis│
   │ Modules │                          │  Module │
   └────┬────┘                          └────┬────┘
        │                                    │
        └────────────┬───────────────────────┘
                     │
              ┌──────▼──────┐
              │  Database   │
              │   SQLite    │
              └──────▲──────┘
                     │
        ┌────────────┴────────────┐
        │      Collectors         │
        │  ┌────────┬────────┐   │
        │  │ DATASUS│ Google │   │
        │  ├────────┼────────┤   │
        │  │  IBGE  │ ReclAq │   │
        │  ├────────┼────────┤   │
        │  │  FBSP  │  INEP  │   │
        │  └────────┴────────┘   │
        └─────────────────────────┘
```

### Fluxo de Dados

1. **Coleta**: Coletores automatizados extraem dados de fontes diversas
2. **Validação**: Cada registro recebe um score de qualidade (0-100)
3. **Processamento**: Análise de sentimentos e categorização temática
4. **Armazenamento**: Dados estruturados no SQLite/PostgreSQL
5. **API**: FastAPI expõe endpoints RESTful
6. **Visualização**: Frontend consome API e renderiza dashboards
7. **Análise**: Geração de insights e relatórios

---

## 📦 Instalação

### Instalação no Windows

#### Passo 1: Instalar o Python

##### Opção A: Instalador Oficial (Recomendado)

1. **Baixar o Python**:
   - Acesse [python.org/downloads](https://www.python.org/downloads/)
   - Clique em "Download Python 3.x.x" (versão 3.8 ou superior)

2. **Executar o Instalador**:
   - Execute o arquivo `.exe` baixado
   - ⚠️ **IMPORTANTE**: Marque a opção "Add Python to PATH" antes de clicar em "Install Now"
   - Aguarde a instalação completar

3. **Verificar a Instalação**:
   ```cmd
   python --version
   ```
   Você deve ver algo como: `Python 3.11.x`

##### Opção B: Microsoft Store (Alternativa)

1. Abra a Microsoft Store
2. Pesquise por "Python 3.11" (ou versão mais recente)
3. Clique em "Obter" ou "Instalar"
4. Aguarde a instalação completar

#### Passo 2: Verificar o pip

O pip geralmente vem instalado automaticamente com o Python. Para verificar:

```cmd
pip --version
```

**Se o pip não estiver instalado:**

1. **Baixar o get-pip.py**:
   - Acesse [bootstrap.pypa.io/get-pip.py](https://bootstrap.pypa.io/get-pip.py)
   - Salve o arquivo (Ctrl+S) como `get-pip.py`

2. **Instalar o pip**:
   ```cmd
   python get-pip.py
   ```

3. **Verificar novamente**:
   ```cmd
   pip --version
   ```

#### Passo 3: Instalar o Git (se não tiver)

1. **Baixar o Git**:
   - Acesse [git-scm.com/download/win](https://git-scm.com/download/win)
   - Baixe o instalador para Windows

2. **Instalar**:
   - Execute o instalador
   - Use as configurações padrão (clique em "Next" até finalizar)

3. **Verificar**:
   ```cmd
   git --version
   ```

#### Passo 4: Clonar o Repositório

Abra o **Prompt de Comando (CMD)** ou **PowerShell** e execute:

```cmd
git clone https://github.com/PedroASenna/Termometro-de-Comentarios-de-Imperatriz-e-regi-o.git
cd Termometro-de-Comentarios-de-Imperatriz-e-regi-o
```

#### Passo 5: Criar Ambiente Virtual

```cmd
python -m venv .venv
```

> 💡 **O que é um ambiente virtual?** É um espaço isolado onde as dependências do projeto ficam separadas do sistema operacional, evitando conflitos entre projetos.

#### Passo 6: Ativar o Ambiente Virtual

**No CMD (Prompt de Comando):**
```cmd
.venv\Scripts\activate
```

**No PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**Se houver erro de execução no PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

> ✅ Quando ativado, você verá `(.venv)` antes do caminho no terminal

#### Passo 7: Instalar as Dependências

```cmd
pip install -r requirements.txt
```

#### Passo 8: Configurar o Projeto

Copie os arquivos de exemplo e edite com suas configurações:

```cmd
copy .env.example .env
copy config.example.json config.json
```

Edite o `.env` e o `config.json` conforme necessário (veja seção [Configuração](#-configuração))

#### Passo 9: Executar o Projeto

**Backend (API):**

> ⚠️ **Importante**: o comando deve ser executado na **raiz do projeto** (não dentro de `backend/`), pois `backend/main.py` usa imports relativos ao pacote `backend`. Rodar `cd backend && uvicorn main:app` resulta em `ImportError: attempted relative import with no known parent package`.

```cmd
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
- Abra o arquivo `frontend/index.html` no navegador
- Ou use um servidor local como Live Server (extensão do VSCode)

#### Desativar o Ambiente Virtual

Quando terminar de trabalhar:

```cmd
deactivate
```

---

### Instalação no Linux/Ubuntu

#### Passo 1: Atualizar o Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

#### Passo 2: Instalar Python e Ferramentas

```bash
sudo apt install python3 python3-pip python3-venv python3-full git -y
```

#### Passo 3: Verificar a Instalação

```bash
python3 --version
pip3 --version
git --version
```

#### Passo 4: Clonar o Repositório

```bash
git clone https://github.com/PedroASenna/Termometro-de-Comentarios-de-Imperatriz-e-regi-o.git
cd Termometro-de-Comentarios-de-Imperatriz-e-regi-o
```

#### Passo 5: Criar e Ativar Ambiente Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> ✅ Quando ativado, você verá `(.venv)` antes do seu prompt

#### Passo 6: Instalar Dependências

```bash
pip install -r requirements.txt
```

#### Passo 7: Configurar o Projeto

```bash
cp .env.example .env
cp config.example.json config.json
nano .env config.json  # ou use seu editor preferido
```

#### Passo 8: Executar o Projeto

**Backend:**

> ⚠️ **Importante**: rode o comando abaixo a partir da **raiz do projeto** (não de dentro de `backend/`). O módulo `backend/main.py` usa imports relativos (`from . import crud, models`), então ele só funciona quando importado como parte do pacote `backend` — `cd backend && uvicorn main:app` falha com `ImportError`.

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
- Abra `frontend/index.html` no navegador
- Ou configure um servidor web (nginx, apache)

#### Desativar o Ambiente Virtual

```bash
deactivate
```

---

### Instalação no macOS

#### Passo 1: Instalar Homebrew (se não tiver)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Passo 2: Instalar Python e Git

```bash
brew install python git
```

#### Passo 3: Verificar Instalação

```bash
python3 --version
pip3 --version
git --version
```

#### Passo 4: Clonar o Repositório

```bash
git clone https://github.com/PedroASenna/Termometro-de-Comentarios-de-Imperatriz-e-regi-o.git
cd Termometro-de-Comentarios-de-Imperatriz-e-regi-o
```

#### Passo 5: Criar e Ativar Ambiente Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Passo 6: Instalar Dependências

```bash
pip install -r requirements.txt
```

#### Passo 7: Configurar e Executar

Siga os mesmos passos do Linux para configuração e execução.

---

## ⚙️ Configuração

### 1. Arquivo `.env`

Copie o exemplo pronto (`cp .env.example .env` ou `copy .env.example .env` no Windows) e ajuste se necessário. Ele já vem com os valores padrão para rodar localmente:

```env
# Banco de dados — lido por backend/database.py
DATABASE_URL=sqlite:///./termometro_ma.db

# Credenciais opcionais, usadas apenas pelos coletores experimentais em src/
# (src/auth.py + src/collectors/*). Não são necessárias para o backend
# principal (backend/ + frontend/).
API_KEY=
API_SECRET=
ACCESS_TOKEN=
ACCESS_TOKEN_SECRET=
BEARER_TOKEN=
```

> ℹ️ `HOST`, `PORT` e afins **não** são lidos automaticamente do `.env` hoje — passe-os diretamente na linha de comando do `uvicorn` (`--host` / `--port`), como nos exemplos deste README.

### 2. Arquivo `config.json`

Este arquivo é lido pelo `PublicOpinionCollector` (via `run_collectors.py`) e define os sites de notícias que serão raspados e as palavras-chave de categorização. Copie o exemplo:

```bash
cp config.example.json config.json
```

```json
{
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
      "enable_comments": true,
      "max_articles": 50
    }
  ],
  "keywords_expansion": {
    "Segurança": ["policia", "crime", "assalto", "roubo"],
    "Saúde": ["hospital", "posto", "sus", "medico"]
  }
}
```

> Se `config.json` não existir, `run_collectors.py` procura automaticamente por `scrapers_config.json` como alternativa.

### 3. Inicializar o Banco de Dados

As tabelas são criadas automaticamente na primeira vez que o backend sobe (`models.Base.metadata.create_all(bind=engine)` roda ao importar `backend/main.py`), então **você normalmente não precisa fazer nada aqui**. Se quiser criar as tabelas manualmente sem subir o servidor (por exemplo, antes de rodar os coletores), execute a partir da raiz do projeto:

```bash
python -c "from backend.database import init_db; init_db()"
```

---

## 🚀 Uso

### Executar Coletores de Dados

`run_collectors.py` não aceita argumentos de linha de comando (`--all`, `--source`, `--city` etc. não existem). Ele sempre roda a coleta completa das 8 fontes em sequência, do zero até o fim:

```bash
python run_collectors.py
```

O progresso de cada fonte é logado no console e em `massive_collection.log`. Se alguma fonte falhar, o script registra o erro e segue para a próxima.

### Executar o Backend (API)

Execute a partir da **raiz do projeto** (veja o aviso na seção de Instalação sobre por que `cd backend` quebra os imports):

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

**Documentação interativa:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Executar o Frontend

1. **Opção 1 - Navegador Direto:**
   - Abra `frontend/index.html` no navegador

2. **Opção 2 - Servidor Local (recomendado):**
   ```bash
   # Com Python
   cd frontend
   python -m http.server 8080
   ```
   Acesse: `http://localhost:8080`

3. **Opção 3 - Live Server (VSCode):**
   - Instale a extensão "Live Server"
   - Clique com botão direito em `index.html`
   - Selecione "Open with Live Server"

---

## 📡 Fontes de Dados

### Fontes Governamentais
1. **DATASUS** - Dados do Sistema Único de Saúde
   - URL: `datasus.saude.gov.br`
   - Dados: Estatísticas de saúde, atendimentos, leitos
   - Atualização: Mensal

2. **IBGE** - Instituto Brasileiro de Geografia e Estatística
   - URL: `ibge.gov.br`
   - Dados: Demografia, economia, infraestrutura
   - Atualização: Anual/Mensal

3. **INEP** - Instituto Nacional de Estudos e Pesquisas Educacionais
   - URL: `inep.gov.br`
   - Dados: Censo escolar, IDEB, matrículas
   - Atualização: Anual

4. **FBSP** - Fórum Brasileiro de Segurança Pública
   - URL: `forumseguranca.org.br`
   - Dados: Criminalidade, violência
   - Atualização: Anual

5. **Portal da Transparência**
   - URL: `portaltransparencia.gov.br`
   - Dados: Gastos públicos, convênios
   - Atualização: Diária

### Fontes Privadas
6. **Google Maps API**
   - Dados: Avaliações de estabelecimentos, POIs
   - Atualização: Tempo real

7. **Reclame Aqui**
   - URL: `reclameaqui.com.br`
   - Dados: Reclamações de empresas locais
   - Atualização: Tempo real

### ⚠️ Nota sobre a origem dos dados

Nem todos os coletores fazem scraping/consumo de API em tempo real hoje. Levantamento do código atual (`backend/collectors/`):

| Coletor | Origem dos dados |
|---|---|
| `news_scraper.py`, `social_media_collector.py` | Scraping real via `requests` + `BeautifulSoup` |
| `structured_data_collector.py` | Consumo real de API HTTP (dados estruturados/IBGE) |
| `google_maps_collector.py`, `datasus_collector.py`, `reclameaqui_collector.py`, `procon_collector.py`, `inep_collector.py`, `transparencia_collector.py` | **Dados sintéticos**: gerados com `random`/templates para simular volume e distribuição realistas (não é scraping ao vivo) |

Isso é importante para quem for usar este repositório como referência ou avaliar os resultados: os números e "tempo real" mencionados neste README refletem o comportamento **pretendido/planejado** do sistema; parte dos coletores ainda precisa ser migrada de dados simulados para coleta real. Se você for citar isso em um trabalho acadêmico, deixe essa distinção explícita.

---

## 🔌 API

> A lista abaixo reflete os endpoints **realmente implementados** em `backend/main.py`. A forma mais confiável de explorar a API é abrir `http://localhost:8000/docs` (Swagger UI) com o servidor rodando — ele é gerado automaticamente a partir do código.

### Endpoints Principais

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Informações gerais da API e lista de endpoints |
| `GET` | `/api/data` | Menções recentes (filtros opcionais: `theme`, `location`, `search_text`; limite fixo de 200 registros, balanceado entre fontes/sentimentos) |
| `GET` | `/api/data/{city_name}` | Todas as menções de uma cidade específica |
| `GET` | `/api/scores` | Contagem de menções negativas por cidade (usado para colorir o mapa) |
| `GET` | `/api/cities` | Lista de cidades com dados disponíveis e total de menções |
| `GET` | `/api/stats/summary` | Estatísticas gerais: total de registros, distribuição por sentimento/tema/fonte, top localidades, intervalo de datas |
| `GET` | `/api/data/filters/options` | Valores possíveis para os filtros do frontend (temas, localidades, fontes, sentimentos) |
| `POST` | `/api/data/analysis` | Análise completa dos dados, aceita um corpo JSON com filtros |
| `POST` | `/api/data/comparison-tables` | Tabelas comparativas entre fontes/temas, aceita filtros no corpo |
| `POST` | `/api/data/filter` | Filtro avançado paginado (até 1000 registros), aceita filtros no corpo |
| `POST` | `/api/data/report` | Relatório textual gerado a partir da análise, aceita filtros no corpo |
| `POST` | `/api/data/populate` | Recria o banco e dispara `run_collectors.py` como subprocesso (operação pesada e demorada) |

**Exemplo — estatísticas gerais:**
```http
GET /api/stats/summary
```
```json
{
  "total_records": 50000,
  "by_sentiment": {"POSITIVO": 12500, "NEGATIVO": 25000, "NEUTRO": 12500},
  "by_theme": {"Saúde": 15000, "Segurança": 12000},
  "by_source": {"DATASUS": 8000, "Google Maps": 7000},
  "by_location": {"Imperatriz": 5234, "São Luís": 4800},
  "date_range": {"earliest": "2024-01-01T00:00:00", "latest": "2025-01-15T10:30:00"}
}
```

### Códigos de Status

- `200 OK`: Sucesso (inclusive para erros de negócio — vários endpoints retornam `{"status": "error", ...}` com HTTP 200 em vez de 4xx/5xx; veja o código-fonte antes de assumir o contrato de erro)
- `404 Not Found`: Rota inexistente
- `422 Unprocessable Entity`: Corpo/parâmetros inválidos (validação do FastAPI)
- `500 Internal Server Error`: Erro não tratado no servidor

---

## 🎨 Frontend

### Páginas Principais

#### 1. Dashboard Principal (`index.html`)
- **Mapa Interativo**: 217 cidades do Maranhão com Leaflet.js
- **Termômetro de Satisfação**: Indicador visual em tempo real
- **Tabelas Comparativas**: Fontes, temas, cidades
- **Gráficos Interativos**: Chart.js com múltiplos tipos
- **Filtros Avançados**: 9 filtros independentes
- **Análise Temporal**: Evolução ao longo do tempo
- **Exportação**: Relatórios e gráficos

#### 2. Análise de Fontes (`Fonte_de_dados.html`)
- Comparação detalhada entre fontes
- Gráficos de distribuição
- Métricas de confiabilidade

### Características do Frontend
- ✅ **Responsivo**: Adaptável a mobile, tablet e desktop
- ✅ **Performance**: Lazy loading e paginação
- ✅ **UX Moderna**: Animações suaves e feedback visual
- ✅ **Acessibilidade**: Seguindo boas práticas WCAG
- ✅ **Fallbacks**: Sistema resiliente a falhas da API

### Tecnologias do Frontend
- **Leaflet.js**: Mapas interativos com camadas personalizadas
- **Chart.js**: Gráficos responsivos (linha, barra, pizza, radar)
- **Vanilla JS**: Sem frameworks pesados, performance otimizada
- **CSS Grid/Flexbox**: Layout moderno e responsivo
- **Font Awesome**: Biblioteca de ícones

---

## 📁 Estrutura do Projeto

```
termometro-comentarios/
├── backend/                     # Sistema atual: API FastAPI + SQLite (é o que este README documenta)
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── data_analyzer.py             # Análise e agregação de dados (SQL)
│   │   ├── datasus_collector.py         # Coletor DATASUS      (dados sintéticos)
│   │   ├── google_maps_collector.py     # Coletor Google Maps  (dados sintéticos)
│   │   ├── inep_collector.py            # Coletor INEP         (dados sintéticos)
│   │   ├── news_scraper.py              # Scraping real de notícias (requests + BeautifulSoup)
│   │   ├── procon_collector.py          # Coletor PROCON       (dados sintéticos)
│   │   ├── public_opinion_collector.py  # Opinião pública, lê config.json/scrapers_config.json
│   │   ├── reclameaqui_collector.py     # Coletor Reclame Aqui (dados sintéticos)
│   │   ├── social_media_collector.py    # Scraping real de redes sociais
│   │   ├── structured_data_collector.py # Consumo real de API de dados estruturados
│   │   └── transparencia_collector.py   # Portal da Transparência (dados sintéticos)
│   ├── __init__.py
│   ├── check_sentiments.py     # Script utilitário de conferência de sentimentos
│   ├── crud.py                 # Operações de leitura/escrita no banco
│   ├── database.py             # Engine SQLAlchemy, sessão, init_db()
│   ├── main.py                 # App FastAPI (rode com `uvicorn backend.main:app` a partir da raiz)
│   └── models.py                # Modelo SQLAlchemy `Mention`
├── frontend/                    # HTML/CSS/JS estático (consumido via API em localhost:8000)
│   ├── css/style.css
│   ├── js/app.js
│   ├── paginas/
│   │   ├── Fonte_de_dados.html
│   │   ├── fonte_de_dados.css
│   │   └── fonte_de_dados.js
│   ├── diagnostico.html
│   ├── ma_cities.geojson        # GeoJSON dos municípios do Maranhão
│   └── index.html               # Página principal (mapa + termômetro)
├── src/                         # ⚠️ Sistema legado/experimental (CLI, Twitter/X, YouTube).
│   │                             #    Não é usado pelo fluxo backend+frontend deste README.
│   ├── collectors/               #    Acionado via `python run.py` → src/main.py
│   ├── auth.py
│   ├── config.py
│   ├── data_cleaner.py
│   ├── data_collector.py
│   ├── data_exporter.py
│   ├── main.py
│   ├── sentiment.py
│   ├── sentiment_analyzer.py
│   ├── utils.py
│   └── visualizer_advanced.py
├── docs/                         # Documentação adicional (arquivos ainda vazios/placeholder)
│   ├── api_documentations.md
│   ├── findings.md
│   └── project_plan.md
├── tests/                        # Estrutura de testes criada, arquivos ainda vazios (ver Roadmap)
│   ├── test_data_collector.py
│   ├── test_sentiment_analysis.py
│   └── test_utils.py
├── dashboard.py                  # Dashboard alternativo em Streamlit, lê arquivos .jsonl (opcional/experimental)
├── data_validator.py             # Validação de valores vindos de fontes externas (IBGE etc.)
├── debug_database.py             # Script de diagnóstico do banco (`python debug_database.py`)
├── test_insert_data.py           # Script para popular o banco com dados de teste
├── Maps_collector.py             # ⚠️ Versão solta/antiga do coletor Google Maps na raiz —
│                                  #    a versão em uso é backend/collectors/google_maps_collector.py
├── install_chrome.py             # Instala Chromium para o Kaleido (requer o pacote `kaleido`,
│                                  #    que não está no requirements.txt — instale à parte se precisar)
├── run.py                        # Entrada do sistema legado (`src/main.py`)
├── run_collectors.py             # Script principal de coleta do backend atual (sem argumentos de CLI)
├── .env.example                  # Template de variáveis de ambiente
├── .gitignore
├── config.example.json           # Template de configuração dos coletores de notícias/opinião
├── requirements.txt              # Dependências Python (organizadas por finalidade)
├── README.md                     # Este arquivo
└── LICENSE                       # Licença MIT
```

> **Por que existem `src/` e vários scripts soltos na raiz?** O projeto evoluiu de um protótipo em linha de comando (`src/`, acionado por `run.py`) para a arquitetura atual (`backend/` + `frontend/`, documentada neste README). Os arquivos soltos na raiz (`dashboard.py`, `Maps_collector.py`, `data_validator.py`, `debug_database.py`, `test_insert_data.py`, `install_chrome.py`) são scripts auxiliares/experimentais de diferentes fases do desenvolvimento — nenhum deles é necessário para seguir os passos de instalação e execução descritos acima. Uma limpeza/organização desses arquivos é uma melhoria futura recomendada (ver [Roadmap](#-roadmap)).

---

## 📈 Análise de Dados

### Categorias Temáticas
O sistema categoriza automaticamente os dados em **8 temas**:

1. 🛡️ **Segurança**: Criminalidade, policiamento, violência
2. 🏗️ **Infraestrutura**: Obras, saneamento, iluminação
3. 🏥 **Saúde**: Hospitais, atendimento, medicamentos
4. 📚 **Educação**: Escolas, professores, qualidade de ensino
5. 🚌 **Transporte**: Ônibus, estradas, trânsito
6. 🏪 **Comércio**: Estabelecimentos, atendimento, preços
7. 👥 **Demografia**: População, estatísticas demográficas
8. 🏛️ **Administração Pública**: Gestão, transparência, serviços

### Classificação de Sentimentos
- **POSITIVO**: Satisfação, elogios, boas experiências
- **NEGATIVO**: Insatisfação, reclamações, problemas
- **NEUTRO**: Informações objetivas, sem carga emocional

### Cálculo do Score de Satisfação
```python
score = (
    (positivos - negativos) / total_menções * 100
    + bonus_qualidade
    - penalidade_fonte
)
score = max(0, min(100, score))  # Limitado entre 0-100
```

### Score de Qualidade dos Dados
Cada registro recebe um score de 0-100 baseado em:
- **Completude** (30%): Campos preenchidos
- **Consistência** (25%): Validação de dados
- **Atualidade** (20%): Recência da informação
- **Confiabilidade da Fonte** (25%): Reputação da fonte

---

## ⚡ Performance

### Otimizações Implementadas

#### Backend
- ✅ **Queries SQL Diretas**: Sem pandas em produção (20x mais rápido)
- ✅ **Índices no Banco**: `source_platform`, `theme`, `location`, `timestamp_utc`
- ✅ **Paginação**: Carregamento sob demanda (padrão: 1000 registros/página)
- ✅ **Cache de Agregações**: Resultados pré-calculados
- ✅ **Conexão Pooling**: Reutilização de conexões SQL
- ✅ **Async/Await**: FastAPI com processamento assíncrono
- ✅ **Bulk Operations**: Inserção em lote (1000+ registros/vez)

#### Frontend
- ✅ **Lazy Loading**: Carregamento progressivo de gráficos
- ✅ **Debounce**: 500ms delay em filtros de busca
- ✅ **Chart.js Performance**: Canvas rendering
- ✅ **Fallback System**: 3 níveis de fallback para filtros
- ✅ **Memoization**: Cache de resultados de API
- ✅ **Virtual Scrolling**: Para grandes listas

### Benchmarks
- **Coleta de Dados**: ~50.000 registros/hora
- **Query Simples**: < 50ms (95th percentile)
- **Query Complexa**: < 200ms (95th percentile)
- **Renderização Mapa**: < 1s para 217 cidades
- **Carregamento Frontend**: < 2s (first contentful paint)
- **Inserção Bulk**: ~10.000 registros/segundo

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga os passos:

### 1. Fork o Projeto
```bash
# Clique em "Fork" no GitHub
```

### 2. Crie uma Branch
```bash
git checkout -b feature/NovaFuncionalidade
```

### 3. Commit suas Mudanças
```bash
git add .
git commit -m "Add: Nova funcionalidade X"
```

**Padrões de Commit:**
- `Add:` Nova funcionalidade
- `Fix:` Correção de bug
- `Update:` Atualização de código existente
- `Refactor:` Refatoração sem mudança de funcionalidade
- `Docs:` Apenas documentação
- `Style:` Formatação, ponto e vírgula, etc
- `Test:` Adição de testes

### 4. Push para a Branch
```bash
git push origin feature/NovaFuncionalidade
```

### 5. Abra um Pull Request
- Descreva suas mudanças detalhadamente
- Referencie issues relacionadas
- Adicione screenshots se aplicável
- Aguarde review

### Diretrizes
- ✅ Código limpo e documentado
- ✅ Testes unitários (quando aplicável)
- ✅ Seguir PEP 8 (Python)
- ✅ Commits descritivos em português
- ✅ Atualizar documentação
- ✅ Manter compatibilidade com Python 3.8+

### Reportar Bugs
Ao reportar bugs, inclua:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Sistema operacional e versão do Python
- Logs de erro (se houver)

---

## 🐛 Resolução de Problemas

### Problemas Comuns

#### 1. Erro ao ativar ambiente virtual no Windows (PowerShell)
```
.venv\Scripts\Activate.ps1 : não pode ser carregado porque a execução de scripts foi desabilitada
```
**Solução:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Módulo não encontrado após instalação
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solução:**
- Verifique se o ambiente virtual está ativado
- Reinstale as dependências: `pip install -r requirements.txt`

#### 3. Erro de conexão com banco de dados
```
sqlalchemy.exc.OperationalError: unable to open database file
```
**Solução:**
- Verifique permissões da pasta
- Crie as tabelas manualmente a partir da raiz do projeto: `python -c "from backend.database import init_db; init_db()"`

#### 3.1. `ImportError: attempted relative import with no known parent package`
Isso acontece se você rodar `cd backend && uvicorn main:app`. `backend/main.py` usa imports relativos e precisa ser executado como parte do pacote `backend`.
**Solução:** rode a partir da raiz do projeto: `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`

#### 4. API não responde
- Verifique se o uvicorn está rodando
- Confirme a porta 8000 está disponível
- Verifique firewall

#### 5. Frontend não carrega dados
- Confirme que a API está rodando em `http://localhost:8000`
- Verifique o console do navegador (F12) para erros
- Teste os endpoints da API diretamente: `http://localhost:8000/docs`

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

```
MIT License

Copyright (c) 2025 Pedro Senna

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👨‍💻 Autor

**Pedro Senna**
- GitHub: [@PedroASenna](https://github.com/PedroASenna)
- LinkedIn: [Pedro Azevedo Sena](https://www.linkedin.com/in/pedro-azevedo-sena-7aa711302/)
- Email: pedrologingt232@gmail.com

---

## 🙏 Agradecimentos

- **Fontes de Dados**: DATASUS, IBGE, FBSP, INEP, Portal da Transparência
- **Bibliotecas Open Source**: FastAPI, SQLAlchemy, BeautifulSoup, Leaflet, Chart.js
- **Comunidade Python**: Pela excelente documentação e suporte
- **Comunidade de Desenvolvedores**: Por feedback e contribuições

---

## 🗺️ Roadmap

### Versão 2.0 (Futuro)
- [ ] Machine Learning para previsão de tendências
- [ ] Dashboard administrativo com autenticação
- [ ] API de integração com outros sistemas
- [ ] App mobile (React Native)
- [ ] Suporte a PostgreSQL e MySQL
- [ ] Autenticação e autorização (OAuth2, JWT)
- [ ] Sistema de notificações em tempo real
- [ ] Export para Power BI / Tableau
- [ ] Análise de imagens (Computer Vision)
- [ ] Chatbot integrado com IA
- [ ] Relatórios automáticos em PDF
- [ ] Integração com redes sociais (Twitter, Facebook)
- [ ] Sistema de alerta para anomalias
- [ ] API GraphQL

### Melhorias Planejadas
- [ ] Testes automatizados (coverage > 80%) — `tests/` já existe mas os arquivos estão vazios
- [ ] CI/CD com GitHub Actions
- [ ] Docker e Docker Compose
- [ ] Documentação em inglês
- [ ] Tutorial em vídeo
- [ ] Performance monitoring (APM)
- [ ] Migrar os coletores que hoje geram dados sintéticos (DATASUS, Google Maps, Reclame Aqui, PROCON, INEP, Portal da Transparência) para coleta/consumo de API real
- [ ] Consolidar ou remover o sistema legado em `src/` e os scripts soltos na raiz (`dashboard.py`, `Maps_collector.py`, `data_validator.py`, `debug_database.py`, `test_insert_data.py`, `install_chrome.py`)
- [ ] Preencher `docs/api_documentations.md`, `docs/findings.md` e `docs/project_plan.md` (atualmente vazios)

---

## 📚 Recursos Adicionais

### Documentação
- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Leaflet.js Docs](https://leafletjs.com/reference.html)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)

### Tutoriais Recomendados
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [REST API Best Practices](https://restfulapi.net/)
- [Web Scraping Ethics](https://www.scrapehero.com/web-scraping-ethics/)

### Comunidade
- [Python Brasil](https://python.org.br/)
- [FastAPI Discord](https://discord.com/invite/fastapi)
- [Stack Overflow - Python](https://stackoverflow.com/questions/tagged/python)

---

## 📊 Estatísticas do Projeto

![GitHub Repo Size](https://img.shields.io/github/repo-size/PedroASenna/Termometro-de-Comentarios-de-Imperatriz-e-regi-o)
![GitHub Last Commit](https://img.shields.io/github/last-commit/PedroASenna/Termometro-de-Comentarios-de-Imperatriz-e-regi-o)
![GitHub Issues](https://img.shields.io/github/issues/PedroASenna/Termometro-de-Comentarios-de-Imperatriz-e-regi-o)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/PedroASenna/Termometro-de-Comentarios-de-Imperatriz-e-regi-o)

---

<div align="center">

**Desenvolvido com ❤️ em Python**

⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!

[![Star on GitHub](https://img.shields.io/github/stars/PedroASenna/Termometro-de-Comentarios-de-Imperatriz-e-regi-o?style=social)](https://github.com/PedroASenna/Termometro-de-Comentarios-de-Imperatriz-e-regi-o)

**[⬆ Voltar ao topo](#-termômetro-de-comentários---imperatriz-e-região)**

</div>
