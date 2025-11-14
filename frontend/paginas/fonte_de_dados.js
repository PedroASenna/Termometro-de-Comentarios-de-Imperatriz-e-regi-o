// ========================================
// ANÁLISE DE DADOS COM GRÁFICOS - TERMÔMETRO DO MARANHÃO
// VERSÃO COMPACTA COM SCROLL
// ========================================

const API_BASE = 'http://127.0.0.1:8000/api';

let currentAnalysis = null;
let comparisonTables = null;
let filterOptions = null;

// Armazena instâncias dos gráficos para poder destruí-los ao atualizar
let chartInstances = {};

// Variáveis para controlar estado de carregamento
let isFiltering = false;
let isLoading = false;

// Variável para debounce da busca
let searchTimeout = null;

// Mapa de Fonte -> Tema e lista de todos os temas
const fonteTemaMap = {
    'DATASUS': ['Saúde'],
    'IBGE_Oficial': ['Demografia', 'Infraestrutura'],
    'IBGE_Demografia': ['Demografia'],
    'FBSP': ['Segurança'],
    'FBSP_Simulado': ['Segurança'],
    'Procon/MP-MA': ['Comércio'],
    'PROCON-MA': ['Comércio'],
    'Google Maps': ['Infraestrutura', 'Comércio', 'Saúde'],
    'google_reviews': ['Infraestrutura', 'Comércio', 'Saúde'],
    'Reclame Aqui': ['Comércio'],
    'INEP': ['Educação'],
    'Portal da Transparência': ['Infraestrutura', 'Segurança'],
    'social_facebook': ['Segurança', 'Infraestrutura', 'Comércio', 'Saúde', 'Educação', 'Transporte'],
    'social_instagram': ['Segurança', 'Infraestrutura', 'Comércio', 'Saúde', 'Educação', 'Transporte'],
    'social_twitter': ['Segurança', 'Infraestrutura', 'Comércio', 'Saúde', 'Educação', 'Transporte'],
    'social_whatsapp_groups': ['Segurança', 'Infraestrutura', 'Comércio', 'Saúde', 'Educação', 'Transporte'],
    'news_portal': ['Segurança', 'Infraestrutura', 'Comércio', 'Saúde', 'Educação', 'Transporte']
};
const todosTemas = ['Segurança', 'Infraestrutura', 'Comércio', 'Saúde', 'Educação', 'Transporte', 'Demografia', 'Administração Pública'];
// Armazena os temas originais carregados da API
let allApiThemes = [];

// <<< INÍCIO DA ATUALIZAÇÃO >>>
// Adicionado um mapa de Fonte -> Localização (baseado no que faz sentido)
const fonteLocationMap = {
    'DATASUS': ['Imperatriz', 'São Luís', 'Açailândia', 'Bacabal', 'Timon'],
    'IBGE_Oficial': ['Imperatriz', 'São Luís', 'Açailândia', 'Bacabal', 'Timon', 'Região Sul', 'Maranhão (Geral)'],
    'IBGE_Demografia': ['Imperatriz', 'São Luís', 'Açailândia', 'Bacabal', 'Timon', 'Região Sul', 'Maranhão (Geral)'],
    'FBSP': ['Maranhão (Geral)', 'São Luís', 'Imperatriz'],
    'FBSP_Simulado': ['Maranhão (Geral)', 'São Luís', 'Imperatriz'],
    'Procon/MP-MA': ['Imperatriz', 'São Luís'],
    'PROCON-MA': ['Imperatriz', 'São Luís'],
    'Google Maps': ['Imperatriz', 'São Luís', 'Açailândia', 'Bacabal', 'Timon'],
    'google_reviews': ['Imperatriz', 'São Luís', 'Açailândia', 'Bacabal', 'Timon'],
    'Reclame Aqui': ['Imperatriz', 'São Luís', 'Açailândia', 'Bacabal', 'Timon'],
    'INEP': ['Imperatriz', 'São Luís', 'Açailândia', 'Bacabal', 'Timon', 'Região Sul', 'Maranhão (Geral)'],
    'Portal da Transparência': ['Maranhão (Geral)', 'Imperatriz', 'São Luís'],
};
// Armazena as localizações originais carregadas da API
let allApiLocations = []; 
// <<< FIM DA ATUALIZAÇÃO >>>


// ========== CONFIGURAÇÃO DOS GRÁFICOS (ESTILO IBGE) ==========
const chartColors = {
    primary: '#20C997',
    secondary: '#0D6EFD',
    tertiary: '#FFC107',
    quaternary: '#DC3545',
    quinary: '#6C757D',
    
    gradient1: ['#20C997', '#17A2B8'],
    gradient2: ['#0D6EFD', '#0056B3'],
    
    themes: {
        'Demografia': '#20C997',
        'Economia': '#0D6EFD',
        'Saúde': '#DC3545',
        'Educação': '#FFC107',
        'Infraestrutura': '#6C757D',
        'Segurança': '#E83E8C',
        'Transporte': '#17A2B8',
        'Outros': '#ADB5BD',
        'Comércio': '#0D6EFD',
        'Administração Pública': '#6C757D'
    }
};

// ========== FUNÇÃO AUXILIAR PARA FETCH COM TIMEOUT ==========
async function fetchWithTimeout(url, options = {}, timeout = 60000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        if (error.name === 'AbortError') {
            throw new Error('Requisição excedeu o tempo limite (60s)');
        }
        throw error;
    }
}

const chartDefaults = {
    font: {
        family: "'Inter', sans-serif",
        size: 11
    },
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'top',
            labels: {
                font: {
                    family: "'Inter', sans-serif",
                    size: 11,
                    weight: '600'
                },
                padding: 10,
                usePointStyle: true
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 10,
            titleFont: {
                size: 12,
                weight: 'bold'
            },
            bodyFont: {
                size: 11
            },
            cornerRadius: 5
        }
    },
    animation: {
        duration: 300
    }
};

// ========== INICIALIZAÇÃO ==========
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🚀 Inicializando sistema de análise compacto...');
    
    // Configura controles de visualização
    setupViewControls();
    
    // Configura listeners dos filtros
    setupFilterListeners();
    
    // Configura estado inicial das seções
    document.querySelectorAll('.section-content').forEach(section => {
        if (section.id === 'source-content') {
            section.classList.remove('collapsed');
            const button = section.previousElementSibling.querySelector('.btn-expand');
            if (button) button.classList.add('rotated');
        } else {
            section.classList.add('collapsed');
        }
    });
    
    // Carrega tudo (opções, análise e dados brutos) com filtros vazios
    await loadFilterOptions();
    await applyFilters();
    
    console.log('✅ Sistema compacto inicializado com sucesso!');
});

// ========== CONFIGURAR LISTENERS DOS FILTROS ==========
function setupFilterListeners() {
    console.log('🎛️ Configurando listeners dos filtros...');
    
    const filterIds = [
        'filter-source', 'filter-theme', 'filter-location',
        'filter-sentiment', 'filter-reliability', 'filter-quality',
        'filter-date-from', 'filter-date-to'
    ];
    
    filterIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', () => {
                console.log(`🔄 Filtro ${id} alterado:`, element.value);
                
                // <<< INÍCIO DA ATUALIZAÇÃO >>>
                if (id === 'filter-source') {
                    // Atualiza ambos os filtros dependentes
                    atualizarTemasDisponiveis(element.value);
                    atualizarLocalizacoesDisponiveis(element.value);
                }
                // <<< FIM DA ATUALIZAÇÃO >>>

                applyFilters();
            });
        }
    });
    
    // Input de busca com debounce
    const searchInput = document.getElementById('filter-search');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                console.log('🔍 Busca alterada:', searchInput.value);
                applyFilters();
            }, 500);
        });
    }
    console.log('✅ Listeners dos filtros configurados');
}

// ========== CONTROLES DE VISUALIZAÇÃO ==========
function setupViewControls() {
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const viewType = this.dataset.view;
            const container = this.dataset.container;
            
            const parentHeader = this.closest('.table-header');
            parentHeader.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            switchView(container, viewType);
        });
    });
}

function switchView(container, viewType) {
     const tableView = document.getElementById(`${container}-table`);
     const chartView = document.getElementById(`${container}-chart`);
     
     if (viewType === 'table') {
         tableView.classList.add('active');
         chartView.classList.remove('active');
     } else if (viewType === 'chart') {
         tableView.classList.remove('active');
         chartView.classList.add('active');
         renderChart(container);
     }
}

function toggleSection(sectionId) {
    const content = document.getElementById(`${sectionId}-content`);
    const button = content.previousElementSibling.querySelector('.btn-expand');
    
    if (content.classList.contains('collapsed')) {
        content.classList.remove('collapsed');
        button.classList.add('rotated');
    } else {
        content.classList.add('collapsed');
        button.classList.remove('rotated');
    }
}

// ========== CARREGAR OPÇÕES DE FILTRO ==========
async function loadFilterOptions() {
    if (isLoading) {
        console.log('⚠️ Já está carregando opções');
        return;
    }
    isLoading = true;
    try {
        console.log('📥 Carregando opções de filtro da API...');
        const response = await fetchWithTimeout(`${API_BASE}/data/filters/options`, {}, 5000);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (data.status === 'success' && data.options) {
            filterOptions = data.options;
            console.log('✅ Opções de filtro carregadas da API:', filterOptions);
            populateFilterSelects();
        } else {
            throw new Error('Resposta da API sem dados válidos');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar opções de filtro da API:', error);
        console.log('🔄 Tentando extrair opções dos dados de comparação...');
        
        // FALLBACK: Extrai opções dos próprios dados
        await extractFilterOptionsFromData();
    } finally {
        isLoading = false;
    }
}

// NOVA FUNÇÃO: Extrai opções de filtro dos dados de comparação
async function extractFilterOptionsFromData() {
    try {
        // Se já tem comparisonTables, usa eles
        if (!comparisonTables) {
            console.log('📥 Carregando dados de comparação para extrair filtros...');
            const response = await fetchWithTimeout(`${API_BASE}/data/comparison`, {}, 10000);
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success' && data.data) {
                    comparisonTables = data.data;
                }
            }
        }
        
        if (comparisonTables) {
            const sources = new Set();
            const themes = new Set();
            const locations = new Set();
            
            // Extrai fontes
            if (comparisonTables.source_comparison && Array.isArray(comparisonTables.source_comparison)) {
                comparisonTables.source_comparison.forEach(item => {
                    if (item.source) sources.add(item.source);
                });
            }
            
            // Extrai temas
            if (comparisonTables.theme_comparison && Array.isArray(comparisonTables.theme_comparison)) {
                comparisonTables.theme_comparison.forEach(item => {
                    if (item.theme) themes.add(item.theme);
                });
            }
            
            // Extrai localizações
            if (comparisonTables.location_comparison && Array.isArray(comparisonTables.location_comparison)) {
                comparisonTables.location_comparison.forEach(item => {
                    if (item.location) locations.add(item.location);
                });
            }
            
            filterOptions = {
                sources: Array.from(sources).sort(),
                themes: Array.from(themes).sort(),
                locations: Array.from(locations).sort()
            };
            
            console.log('✅ Opções extraídas dos dados:', {
                fontes: filterOptions.sources.length,
                temas: filterOptions.themes.length,
                localizações: filterOptions.locations.length
            });
            console.log('📊 Fontes disponíveis:', filterOptions.sources);
            console.log('📊 Temas disponíveis:', filterOptions.themes);
            console.log('📊 Localizações disponíveis:', filterOptions.locations);
            
            populateFilterSelects();
        } else {
            // Se ainda não tem dados, usa listas hardcoded como último recurso
            console.warn('⚠️ Usando opções hardcoded como último recurso');
            filterOptions = {
                sources: ['DATASUS', 'IBGE_Oficial', 'FBSP', 'Google Maps', 'Reclame Aqui', 'INEP', 'Portal da Transparência'],
                themes: ['Saúde', 'Demografia', 'Segurança', 'Infraestrutura', 'Comércio', 'Educação', 'Transporte'],
                locations: ['São Luís', 'Imperatriz', 'Açailândia', 'Bacabal', 'Timon']
            };
            populateFilterSelects();
        }
    } catch (error) {
        console.error('❌ Erro ao extrair opções dos dados:', error);
        // Último recurso: listas hardcoded
        filterOptions = {
            sources: ['DATASUS', 'IBGE_Oficial', 'FBSP', 'Google Maps', 'Reclame Aqui', 'INEP'],
            themes: ['Saúde', 'Demografia', 'Segurança', 'Infraestrutura', 'Comércio', 'Educação'],
            locations: ['São Luís', 'Imperatriz', 'Açailândia', 'Bacabal', 'Timon']
        };
        populateFilterSelects();
    }
}


function populateFilterSelects() {
    if (!filterOptions) {
        console.warn('⚠️ filterOptions não está disponível');
        return;
    }
    
    console.log('📝 Populando selects de filtro...', filterOptions);
    
    const sourceSelect = document.getElementById('filter-source');
    if (sourceSelect && filterOptions.sources) {
        while (sourceSelect.options.length > 1) sourceSelect.remove(1);
        filterOptions.sources.forEach(source => {
            const option = document.createElement('option');
            option.value = source;
            option.textContent = source;
            sourceSelect.appendChild(option);
        });
    }
    
    const themeSelect = document.getElementById('filter-theme');
    if (themeSelect && filterOptions.themes) {
        while (themeSelect.options.length > 1) themeSelect.remove(1);
        
        allApiThemes = filterOptions.themes; // Salva lista completa
        
        filterOptions.themes.forEach(theme => {
            const option = document.createElement('option');
            option.value = theme;
            option.textContent = theme;
            themeSelect.appendChild(option);
        });
    }
    
    const locationSelect = document.getElementById('filter-location');
    if (locationSelect && filterOptions.locations) {
        while (locationSelect.options.length > 1) locationSelect.remove(1);
        
        allApiLocations = filterOptions.locations; // <<< ATUALIZAÇÃO: Salva lista completa
        
        filterOptions.locations.forEach(location => {
            const option = document.createElement('option');
            option.value = location;
            option.textContent = location;
            locationSelect.appendChild(option);
        });
    }
    
    console.log('✅ Selects populados com sucesso');
}

// FUNÇÃO PARA ATUALIZAR TEMAS
function atualizarTemasDisponiveis(fonteSelecionada) {
    const temaSelect = document.getElementById('filter-theme');
    if (!temaSelect) return;

    const temaAtual = temaSelect.value;
    
    while (temaSelect.options.length > 1) {
        temaSelect.remove(1);
    }

    let temasPermitidos = [];

    // Se nenhuma fonte ou "Todos" for selecionado, usa a lista completa da API
    if (!fonteSelecionada || fonteSelecionada === '' || fonteSelecionada === 'Todos') {
        temasPermitidos = allApiThemes;
        console.log('📋 Mostrando TODOS os temas da API');
    } else {
        // Caso contrário, usa o mapa. Se não achar, usa todos os temas como fallback
        temasPermitidos = fonteTemaMap[fonteSelecionada] || allApiThemes;
        console.log(`🔄 Fonte: "${fonteSelecionada}" → Temas permitidos: ${temasPermitidos.join(', ')}`);
    }

    // Popula o select apenas com os temas permitidos que existem na lista da API
    allApiThemes.forEach(theme => {
        if (temasPermitidos.includes(theme)) {
            const option = document.createElement('option');
            option.value = theme;
            option.textContent = theme;
            temaSelect.appendChild(option);
        }
    });

    // Tenta manter a seleção anterior se ela ainda for válida
    const temaAindaDisponivel = Array.from(temaSelect.options).some(opt => opt.value === temaAtual);
    
    if (temaAindaDisponivel) {
        temaSelect.value = temaAtual;
    } else {
        temaSelect.value = ''; // Reseta para "Todos os temas"
        console.log('⚠️ Tema anterior não disponível, resetado para "Todos"');
    }
}

// <<< INÍCIO DA ATUALIZAÇÃO >>>
// NOVA FUNÇÃO para atualizar localizações dinamicamente
function atualizarLocalizacoesDisponiveis(fonteSelecionada) {
    const locationSelect = document.getElementById('filter-location');
    if (!locationSelect) return;

    const localAtual = locationSelect.value;
    
    while (locationSelect.options.length > 1) {
        locationSelect.remove(1);
    }

    let locaisPermitidos = [];

    // Se nenhuma fonte ou "Todos" for selecionado, usa a lista completa da API
    if (!fonteSelecionada || fonteSelecionada === '' || fonteSelecionada === 'Todos') {
        locaisPermitidos = allApiLocations;
        console.log('📋 Mostrando TODAS as localizações da API');
    } else {
        // Caso contrário, usa o mapa. Se não achar, usa todas as localizações como fallback
        locaisPermitidos = fonteLocationMap[fonteSelecionada] || allApiLocations;
        console.log(`🔄 Fonte: "${fonteSelecionada}" → Locais permitidos: ${locaisPermitidos.join(', ')}`);
    }

    // Popula o select apenas com os locais permitidos que existem na lista da API
    allApiLocations.forEach(location => {
        if (locaisPermitidos.includes(location)) {
            const option = document.createElement('option');
            option.value = location;
            option.textContent = location;
            locationSelect.appendChild(option);
        }
    });

    // Tenta manter a seleção anterior se ela ainda for válida
    const localAindaDisponivel = Array.from(locationSelect.options).some(opt => opt.value === localAtual);
    
    if (localAindaDisponivel) {
        locationSelect.value = localAtual;
    } else {
        locationSelect.value = ''; // Reseta para "Todas as cidades"
        console.log('⚠️ Localização anterior não disponível, resetado para "Todos"');
    }
}
// <<< FIM DA ATUALIZAÇÃO >>>

// ========== APLICAR FILTROS (FUNÇÃO PRINCIPAL ATUALIZADA) ==========
async function applyFilters() {
    if (isFiltering) {
        console.log('⚠️ Já está filtrando, aguardando...');
        return;
    }
    isFiltering = true;
    
    const filters = {
        source: document.getElementById('filter-source')?.value || '',
        theme: document.getElementById('filter-theme')?.value || '',
        location: document.getElementById('filter-location')?.value || '',
        sentiment: document.getElementById('filter-sentiment')?.value || '',
        reliability: document.getElementById('filter-reliability')?.value || '',
        min_quality: document.getElementById('filter-quality')?.value || '0',
        date_from: document.getElementById('filter-date-from')?.value || '',
        date_to: document.getElementById('filter-date-to')?.value || '',
        search_text: document.getElementById('filter-search')?.value || ''
    };
    
    const activeFilters = {};
    Object.keys(filters).forEach(key => {
        if (filters[key] && filters[key] !== '') {
             if(key === 'min_quality' && filters[key] === '0') return;
             if(filters[key] === 'Todos') return;

            activeFilters[key] = filters[key];
        }
    });
    
    console.log('🔍 Aplicando filtros:', activeFilters);
    
    showLoadingMetrics();
    const resultsCount = document.getElementById('results-count');
    const fullDataTable = document.getElementById('full-data-table');
    if (resultsCount) resultsCount.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando análise...';
    if (fullDataTable) fullDataTable.innerHTML = getLoadingStateHTML('Aplicando filtros...');

    Object.keys(chartInstances).forEach(key => {
        if (chartInstances[key]) {
            chartInstances[key].destroy();
            chartInstances[key] = null;
        }
    });
    
    renderAllTables(true); // Limpa as tabelas com estado de "loading"

    try {
        const [analysisRes, tablesRes, dataRes] = await Promise.all([
            fetchWithTimeout(`${API_BASE}/data/analysis`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(activeFilters)
            }),
            fetchWithTimeout(`${API_BASE}/data/comparison-tables`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(activeFilters)
            }),
            fetchWithTimeout(`${API_BASE}/data/filter`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(activeFilters)
            })
        ]);

        // Processa Análise (Métricas)
        if (analysisRes.ok) {
            const analysisData = await analysisRes.json();
            if (analysisData.status === 'success') {
                currentAnalysis = analysisData.analysis;
                updateMetricsDisplay();
                if (resultsCount) resultsCount.textContent = `Mostrando ${currentAnalysis.total_records.toLocaleString('pt-BR')} registros`;
                console.log('✅ Análise carregada');
            } else {
                throw new Error(`Análise falhou: ${analysisData.message}`);
            }
        } else {
            throw new Error(`Erro HTTP na Análise: ${analysisRes.status}`);
        }

        // Processa Tabelas (Gráficos)
        if (tablesRes.ok) {
            const tablesData = await tablesRes.json();
            if (tablesData.status === 'success') {
                comparisonTables = tablesData.tables;
                
                renderAllTables();
                renderAllCharts();
                console.log('✅ Tabelas carregadas');
            } else {
                throw new Error(`Tabelas falharam: ${tablesData.error}`);
            }
        } else {
            throw new Error(`Erro HTTP nas Tabelas: ${tablesRes.status}`);
        }

        // Processa Dados Brutos
        if (dataRes.ok) {
            const dataData = await dataRes.json();
            if (dataData.status === 'success') {
                renderFullDataTable(dataData.data);
                console.log(`✅ ${dataData.total} registros carregados`);
            } else {
                throw new Error(`Dados falharam: ${dataData.error}`);
            }
        } else {
            throw new Error(`Erro HTTP nos Dados: ${dataRes.status}`);
        }
        
        document.getElementById('last-update').textContent = new Date().toLocaleString('pt-BR');

    } catch (error) {
        console.error('❌ Erro ao aplicar filtros:', error);
        if (resultsCount) resultsCount.innerHTML = `<span style="color: var(--danger);">❌ Erro: ${error.message}</span>`;
        if (fullDataTable) fullDataTable.innerHTML = getEmptyStateHTML(error.message, true);
        showError(error.message);
    } finally {
        isFiltering = false;
    }
}

function resetFilters() {
    console.log('🔄 Resetando filtros...');
    
    document.getElementById('filter-source').value = '';
    document.getElementById('filter-theme').value = '';
    document.getElementById('filter-location').value = '';
    document.getElementById('filter-sentiment').value = '';
    document.getElementById('filter-reliability').value = '';
    document.getElementById('filter-quality').value = '0';
    document.getElementById('filter-date-from').value = '';
    document.getElementById('filter-date-to').value = '';
    document.getElementById('filter-search').value = '';
    
    // <<< INÍCIO DA ATUALIZAÇÃO >>>
    // Reseta ambos os filtros dinâmicos
    atualizarTemasDisponiveis('');
    atualizarLocalizacoesDisponiveis('');
    // <<< FIM DA ATUALIZAÇÃO >>>

    applyFilters();
    
    console.log('✅ Filtros resetados');
}

// ========== ATUALIZAR MÉTRICAS ==========
function updateMetricsDisplay() {
    if (!currentAnalysis) {
        showLoadingMetrics();
        return;
    };
    
    document.getElementById('total-records').textContent = 
        (currentAnalysis.total_records || 0).toLocaleString('pt-BR');
    
    document.getElementById('high-quality').textContent = 
        (currentAnalysis.quality_metrics?.high_quality_count || 0).toLocaleString('pt-BR');
    
    document.getElementById('avg-quality').textContent = 
        currentAnalysis.quality_metrics?.average_score || 0;
    
    const reliability = currentAnalysis.by_reliability?.high;
    document.getElementById('high-reliability').textContent = 
        `${reliability?.percentage || 0}%`;
}

function showLoadingMetrics() {
    document.getElementById('total-records').textContent = '...';
    document.getElementById('high-quality').textContent = '...';
    document.getElementById('avg-quality').textContent = '...';
    document.getElementById('high-reliability').textContent = '...';
}

// ========== RENDERIZAR TODAS AS TABELAS ==========
function renderAllTables(clear = false) {
    if (clear) {
        document.getElementById('source-table').innerHTML = getLoadingStateHTML();
        document.getElementById('theme-table').innerHTML = getLoadingStateHTML();
        document.getElementById('location-table').innerHTML = getLoadingStateHTML();
        document.getElementById('temporal-table').innerHTML = getLoadingStateHTML();
        return;
    }

    if (!comparisonTables) {
        console.warn("Nenhuma tabela comparativa para renderizar.");
        return;
    }
    
    renderSourceComparisonTable(comparisonTables.source_comparison);
    renderThemeComparisonTable(comparisonTables.theme_comparison);
    renderLocationComparisonTable(comparisonTables.location_comparison);
    renderTemporalAnalysisTable(comparisonTables.temporal_analysis);
    
}

// ========== RENDERIZAR TODOS OS GRÁFICOS ==========
function renderAllCharts() {
    renderChart('source');
    renderChart('theme');
    renderChart('location');
    renderChart('temporal');
}

function renderChart(container) {
    if (chartInstances[container]) {
        chartInstances[container].destroy();
        chartInstances[container] = null;
    }
    
    const chartView = document.getElementById(`${container}-chart`);
    if(chartView) {
         chartView.innerHTML = `<canvas id="${container}-chart-canvas"></canvas>`;
    } else {
        console.error(`Container de gráfico #${container}-chart não encontrado.`);
        return;
    }
    
    switch(container) {
        case 'source':
            renderSourceChart();
            break;
        case 'theme':
            renderThemeChart();
            break;
        case 'location':
            renderLocationChart();
            break;
        case 'temporal':
            renderTemporalChart();
            break;
    }
}

function renderSourceChart() {
    const canvas = document.getElementById('source-chart-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    if (!comparisonTables || !comparisonTables.source_comparison || comparisonTables.source_comparison.length === 0) {
        canvas.parentElement.innerHTML = getEmptyStateHTML('Nenhum dado para o gráfico de fontes.');
        return;
    }
    
    const data = comparisonTables.source_comparison.slice(0, 8);
    
    chartInstances.source = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.source),
            datasets: [
                {
                    label: 'Total',
                    data: data.map(d => d.total),
                    backgroundColor: chartColors.primary,
                    borderRadius: 4,
                    yAxisID: 'y'
                },
                {
                    label: 'Qualidade',
                    data: data.map(d => d.avg_quality),
                    backgroundColor: chartColors.secondary,
                    borderRadius: 4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    grid: { display: true, drawBorder: false }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 100,
                    grid: { display: false }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

function renderThemeChart() {
    const canvas = document.getElementById('theme-chart-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    if (!comparisonTables || !comparisonTables.theme_comparison || comparisonTables.theme_comparison.length === 0) {
        canvas.parentElement.innerHTML = getEmptyStateHTML('Nenhum dado para o gráfico de temas.');
        return;
    }
    
    const data = comparisonTables.theme_comparison;
    
    chartInstances.theme = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.theme),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: data.map(d => chartColors.themes[d.theme] || chartColors.quinary),
                borderWidth: 1,
                borderColor: '#fff'
            }]
        },
        options: {
            ...chartDefaults,
            cutout: '55%'
        }
    });
}

function renderLocationChart() {
    const canvas = document.getElementById('location-chart-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    if (!comparisonTables || !comparisonTables.location_comparison || comparisonTables.location_comparison.length === 0) {
        canvas.parentElement.innerHTML = getEmptyStateHTML('Nenhum dado para o gráfico de cidades.');
        return;
    }
    
    const data = comparisonTables.location_comparison.slice(0, 12).reverse();
    
    chartInstances.location = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.location),
            datasets: [{
                label: 'Total',
                data: data.map(d => d.total),
                backgroundColor: chartColors.primary,
                borderRadius: 4
            }]
        },
        options: {
            ...chartDefaults,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { display: true, drawBorder: false }
                },
                y: {
                    grid: { display: false }
                }
            }
        }
    });
}

function renderTemporalChart() {
    const canvas = document.getElementById('temporal-chart-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    if (!comparisonTables || !comparisonTables.temporal_analysis || comparisonTables.temporal_analysis.length === 0) {
        canvas.parentElement.innerHTML = getEmptyStateHTML('Nenhum dado para o gráfico temporal.');
        return;
    }
    
    const data = comparisonTables.temporal_analysis;
    
    chartInstances.temporal = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => formatDate(d.date)),
            datasets: [
                {
                    label: 'Quantidade',
                    data: data.map(d => d.count),
                    borderColor: chartColors.primary,
                    backgroundColor: 'rgba(32, 201, 151, 0.1)',
                    tension: 0.3,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Qualidade',
                    data: data.map(d => d.avg_quality),
                    borderColor: chartColors.secondary,
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.3,
                    fill: false,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    grid: { display: true, drawBorder: false }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 100,
                    grid: { display: false }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

// ========== FUNÇÕES DE TABELAS ==========
function renderSourceComparisonTable(data) {
    const container = document.getElementById('source-table');
    
    if (!data || data.length === 0) {
        container.innerHTML = getEmptyStateHTML();
        return;
    }
    
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Fonte</th>
                    <th>Total</th>
                    <th>Qualidade</th>
                    <th>Min/Max</th>
                    <th>Positivo</th>
                    <th>Negativo</th>
                    <th>Neutro</th>
                    <th>Confiab.</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.forEach(row => {
        html += `
            <tr>
                <td><strong>${row.source}</strong></td>
                <td>${row.total.toLocaleString('pt-BR')}</td>
                <td><span class="${getQualityBadgeClass(row.avg_quality)}">${row.avg_quality}</span></td>
                <td>${row.min_quality}-${row.max_quality}</td>
                <td><span style="color: var(--success);">${row.positive_rate}%</span></td>
                <td><span style="color: var(--danger);">${row.negative_rate}%</span></td>
                <td><span style="color: var(--gray-500);">${row.neutral_rate}%</span></td>
                <td><span class="${getReliabilityBadgeClass(row.reliability)}">${translateReliability(row.reliability)}</span></td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function renderThemeComparisonTable(data) {
    const container = document.getElementById('theme-table');
    
    if (!data || data.length === 0) {
        container.innerHTML = getEmptyStateHTML();
        return;
    }
    
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Tema</th>
                    <th>Total</th>
                    <th>Fontes</th>
                    <th>Qualidade</th>
                    <th>Pos</th>
                    <th>Neg</th>
                    <th>Neu</th>
                    <th>Balance</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.forEach(row => {
        html += `
            <tr>
                <td><strong>${row.theme}</strong></td>
                <td>${row.count.toLocaleString('pt-BR')}</td>
                <td>${row.sources_count}</td>
                <td><span class="${getQualityBadgeClass(row.avg_quality)}">${row.avg_quality}</span></td>
                <td><span class="sentiment-badge sentiment-positive">${row.positive}</span></td>
                <td><span class="sentiment-badge sentiment-negative">${row.negative}</span></td>
                <td><span class="sentiment-badge sentiment-neutral">${row.neutral}</span></td>
                <td><span style="color: ${row.sentiment_balance > 0 ? 'var(--success)' : 'var(--danger)'};">${row.sentiment_balance}%</span></td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function renderLocationComparisonTable(data) {
    const container = document.getElementById('location-table');
    
    if (!data || data.length === 0) {
        container.innerHTML = getEmptyStateHTML();
        return;
    }
    
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Cidade</th>
                    <th>Total</th>
                    <th>Qualidade</th>
                    <th>Positivo</th>
                    <th>Tema Principal</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.forEach(row => {
        html += `
            <tr>
                <td><strong>${row.location}</strong></td>
                <td>${row.total.toLocaleString('pt-BR')}</td>
                <td><span class="${getQualityBadgeClass(row.avg_quality)}">${row.avg_quality}</span></td>
                <td><span style="color: var(--success);">${row.positive_rate}%</span></td>
                <td>${row.main_theme}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function renderTemporalAnalysisTable(data) {
    const container = document.getElementById('temporal-table');
    
    if (!data || data.length === 0) {
        container.innerHTML = getEmptyStateHTML();
        return;
    }
    
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Qtd</th>
                    <th>Qualidade</th>
                    <th>Positivo</th>
                    <th>Gráfico</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    const maxCount = Math.max(...data.map(d => d.count), 1);
    
    data.forEach(row => {
        const barWidth = Math.min(100, (row.count / maxCount) * 100);
        
        html += `
            <tr>
                <td><strong>${formatDate(row.date)}</strong></td>
                <td>${row.count.toLocaleString('pt-BR')}</td>
                <td><span class="${getQualityBadgeClass(row.avg_quality)}">${row.avg_quality}</span></td>
                <td><span style="color: var(--success);">${row.positive_rate}%</span></td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${barWidth}%"></div>
                    </div>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function renderFullDataTable(data) {
    const container = document.getElementById('full-data-table');
    
    if (!data || data.length === 0) {
        container.innerHTML = getEmptyStateHTML('Nenhum dado encontrado com os filtros aplicados.');
        return;
    }
    
    let html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Fonte</th>
                    <th>Tema</th>
                    <th>Texto</th>
                    <th>Sent.</th>
                    <th>Local</th>
                    <th>Qual.</th>
                    <th>Conf.</th>
                    <th>Data</th>
                    <th>Problemas</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    const limitedData = data.slice(0, 500);
    
    limitedData.forEach(row => {
        html += `
            <tr>
                <td>${row.id}</td>
                <td><small>${row.source_platform}</small></td>
                <td>${row.theme}</td>
                <td style="max-width: 300px; white-space: normal; font-size: 0.75rem;">${truncateText(row.text, 120)}</td>
                <td><span class="${getSentimentBadgeClass(row.sentiment)}">${row.sentiment}</span></td>
                <td>${row.location}</td>
                <td><span class="${getQualityBadgeClass(row.quality_score)}">${row.quality_score}</span></td>
                <td><span class="${getReliabilityBadgeClass(row.reliability)}">${translateReliability(row.reliability)}</span></td>
                <td><small>${formatDate(row.timestamp_utc)}</small></td>
                <td style="max-width: 120px; white-space: normal;"><small style="color: ${row.issues && row.issues !== 'Nenhum problema' ? 'var(--warning)' : 'var(--gray-500)'};">${row.issues || 'Nenhum'}</small></td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';

    if (data.length > 500) {
        html += `<div style="padding: 0.8rem; text-align: center; font-weight: 600; color: var(--gray-500); font-size: 0.8rem;">Mostrando 500 de ${data.length.toLocaleString('pt-BR')} registros.</div>`;
    }

    container.innerHTML = html;
}

// ========== EXPORTAR RELATÓRIO ==========
async function exportReport() {
    try {
        const filters = getActiveFilters();
        
        const response = await fetch(`${API_BASE}/data/report`, {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify(filters)
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            const blob = new Blob([data.report], { type: 'text/plain;charset=utf-8' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `relatorio-termometro-ma-${new Date().toISOString().split('T')[0]}.txt`;
            a.click();
            window.URL.revokeObjectURL(url);
            
            console.log('✅ Relatório exportado');
        } else {
             throw new Error(data.error || "Erro desconhecido");
        }
    } catch (error) {
        console.error('❌ Erro ao exportar relatório:', error);
        alert('Erro ao exportar relatório. Tente novamente.');
    }
}

function getActiveFilters() {
    const filters = {
        source: document.getElementById('filter-source')?.value || '',
        theme: document.getElementById('filter-theme')?.value || '',
        location: document.getElementById('filter-location')?.value || '',
        sentiment: document.getElementById('filter-sentiment')?.value || '',
        reliability: document.getElementById('filter-reliability')?.value || '',
        min_quality: document.getElementById('filter-quality')?.value || '0',
        date_from: document.getElementById('filter-date-from')?.value || '',
        date_to: document.getElementById('filter-date-to')?.value || '',
        search_text: document.getElementById('filter-search')?.value || ''
    };
    
    const activeFilters = {};
    Object.keys(filters).forEach(key => {
        if (filters[key] && filters[key] !== '0' && filters[key] !== '' && filters[key] !== 'Todos') {
            activeFilters[key] = filters[key];
        }
    });
    return activeFilters;
}

// ========== ATUALIZAR DADOS ==========
async function refreshData() {
    console.log('🔄 Atualizando dados...');
    await applyFilters();
}

// ========== FUNÇÕES AUXILIARES ==========
function getQualityBadgeClass(score) {
    if (!score) score = 0;
    score = Number(score);
    if (score >= 85) return 'quality-badge quality-excellent';
    if (score >= 70) return 'quality-badge quality-good';
    if (score >= 50) return 'quality-badge quality-medium';
    return 'quality-badge quality-low';
}

function getSentimentBadgeClass(sentiment) {
    if (sentiment === 'POSITIVO') return 'sentiment-badge sentiment-positive';
    if (sentiment === 'NEGATIVO') return 'sentiment-badge sentiment-negative';
    return 'sentiment-badge sentiment-neutral';
}

function getReliabilityBadgeClass(reliability) {
    if (reliability === 'high') return 'reliability-badge reliability-high';
    if (reliability === 'medium') return 'reliability-badge reliability-medium';
    return 'reliability-badge reliability-low';
}

function translateReliability(reliability) {
    const translations = {
        'high': 'Alta',
        'medium': 'Média',
        'low': 'Baixa'
    };
    return translations[reliability] || reliability;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString.split('T')[0];
        return date.toLocaleDateString('pt-BR', { timeZone: 'UTC' });
    } catch {
        return dateString;
    }
}

function truncateText(text, maxLength) {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function getEmptyStateHTML(message = 'Nenhum dado encontrado.', isError = false) {
    const icon = isError ? 'fa-exclamation-triangle' : 'fa-inbox';
    const color = isError ? 'var(--danger)' : 'var(--gray-400)';
    
    return `
        <div class="empty-state" style="color: ${color};">
            <i class="fas ${icon}"></i>
            <p>${message}</p>
        </div>
    `;
}

function getLoadingStateHTML(message = 'Carregando...') {
    return `
        <div class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>${message}</p>
        </div>
    `;
}

function showError(message) {
    console.error(message);
    const resultsCount = document.getElementById('results-count');
    if (resultsCount) {
        resultsCount.innerHTML = `<span style="color: var(--danger);">❌ Erro: ${message}</span>`;
    }
}

// ========== EXPORTAR FUNÇÕES GLOBAIS ==========
window.applyFilters = applyFilters;
window.resetFilters = resetFilters;
window.toggleSection = toggleSection;
window.exportReport = exportReport;
window.refreshData = refreshData;

console.log('✅ Sistema compacto carregado!');