document.addEventListener("DOMContentLoaded", async function() {
    // Variáveis globais
    let map;
    let geojsonData = null;
    let cityLayers = {};
    let cityNames = [];
    let allMentionsData = [];
    let mapLayer = null; // Camada do mapa para controle

    // Configurações
    const API_BASE_URL = 'http://127.0.0.1:8000/api';
    const GEOJSON_PATH = './ma_cities.geojson';

    // ==========================================
    // INICIALIZAR MAPA (SEM DEFINIR POSIÇÃO)
    // ==========================================
    function initMap() {
        // Cria o mapa com coordenadas baseadas no diagnóstico
        map = L.map('map', {
            zoomControl: false,
            minZoom: 5,
            maxZoom: 13,
            preferCanvas: true
        }).setView([-4.0, -45.15], 7); // Centro calculado do GeoJSON atual
        
        // Adiciona controles
        L.control.zoom({ position: 'topleft' }).addTo(map);
        
        // Tile layer moderno
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | <a href="https://carto.com/">CARTO</a>',
            maxZoom: 20
        }).addTo(map);
        
        console.log('✅ Mapa criado e centralizado em [-4.0, -45.15]');
    }

    // ==========================================
    // CORES BASEADAS NO SCORE
    // ==========================================
    function getScoreColor(score) {
        if (score > 10) return '#ef4444';
        if (score > 5) return '#f59e0b';
        if (score > 2) return '#fbbf24';
        return '#10b981';
    }
    
    function getScoreBorderColor(score) {
        if (score > 10) return '#dc2626';
        if (score > 5) return '#d97706';
        if (score > 2) return '#f59e0b';
        return '#059669';
    }

    // ==========================================
    // RENDERIZAR MAPA
    // ==========================================
    async function renderMapScores() {
        if (!geojsonData || !map) {
            console.error('❌ Dados não disponíveis para renderizar');
            return;
        }

        console.log('🗺️ Buscando scores...');
        const scores = await fetchData('scores');
        
        if (!scores) {
            console.error("❌ Scores não carregados");
            return;
        }

        console.log(`✅ ${Object.keys(scores).length} scores recebidos`);

        // Remove camada antiga se existir
        if (mapLayer) {
            map.removeLayer(mapLayer);
        }

        // Limpa cityLayers
        cityLayers = {};

        // Cria a camada GeoJSON
        mapLayer = L.geoJSON(geojsonData, {
            style: feature => {
                const score = scores[feature.properties.name] || 0;
                return {
                    fillColor: getScoreColor(score),
                    weight: 2,
                    opacity: 1,
                    color: getScoreBorderColor(score),
                    fillOpacity: 0.8
                };
            },
            onEachFeature: (feature, layer) => {
                const cityName = feature.properties.name;
                const score = scores[cityName] || 0;
                cityLayers[cityName] = layer;
                
                // Hover
                layer.on('mouseover', function() {
                    layer.setStyle({
                        weight: 3,
                        fillOpacity: 0.95,
                        color: '#ffffff'
                    });
                    layer.bringToFront();
                });
                
                layer.on('mouseout', function() {
                    layer.setStyle({
                        weight: 2,
                        fillOpacity: 0.8,
                        color: getScoreBorderColor(score)
                    });
                });
                
                // Click
                layer.on('click', function() {
                    document.getElementById('search-box').value = cityName;
                    layer.setStyle({ weight: 4, fillOpacity: 1 });
                    setTimeout(() => {
                        layer.setStyle({ weight: 2, fillOpacity: 0.8 });
                    }, 200);
                    applyFiltersAndRender();
                });
                
                // Tooltip
                let emoji = '🟢', riskLevel = 'Seguro';
                if (score > 10) { emoji = '🔴'; riskLevel = 'Alto Risco'; }
                else if (score > 5) { emoji = '🟡'; riskLevel = 'Atenção'; }
                else if (score > 2) { emoji = '🟠'; riskLevel = 'Cuidado'; }
                
                layer.bindTooltip(`
                    <div style="font-family: 'Inter', sans-serif; padding: 0.25rem;">
                        <div style="font-weight: 700; font-size: 1rem; margin-bottom: 0.25rem;">
                            ${emoji} ${cityName}
                        </div>
                        <div style="font-size: 0.85rem; color: #6b7280;">
                            <strong>Status:</strong> ${riskLevel}<br>
                            <strong>Menções Negativas:</strong> ${score}
                        </div>
                    </div>
                `, {
                    permanent: false,
                    sticky: true,
                    className: 'custom-tooltip',
                    direction: 'top'
                });
            }
        });

        // Adiciona ao mapa
        mapLayer.addTo(map);

        // *** AJUSTE CRÍTICO: Força o mapa a se ajustar APÓS adicionar a camada ***
        setTimeout(() => {
            const bounds = mapLayer.getBounds();
            
            // Log dos bounds para diagnóstico
            console.log('📐 Bounds do GeoJSON:');
            console.log(`   Norte: ${bounds.getNorth().toFixed(3)}°`);
            console.log(`   Sul: ${bounds.getSouth().toFixed(3)}°`);
            console.log(`   Leste: ${bounds.getEast().toFixed(3)}°`);
            console.log(`   Oeste: ${bounds.getWest().toFixed(3)}°`);
            
            // Ajusta o mapa
            map.fitBounds(bounds, {
                padding: [30, 30],
                animate: false // Desativa animação inicial
            });
            
            console.log('✅ Mapa ajustado aos bounds do GeoJSON');
        }, 100);
    }

    // ==========================================
    // ZOOM PARA CIDADE
    // ==========================================
    function zoomToCity(cityName) {
        if (!cityName || cityName === "Maranhão") {
            if (mapLayer) {
                map.fitBounds(mapLayer.getBounds(), {
                    padding: [30, 30],
                    animate: true,
                    duration: 0.5
                });
            }
        } else if (cityLayers[cityName]) {
            map.fitBounds(cityLayers[cityName].getBounds(), {
                padding: [80, 80],
                maxZoom: 10,
                animate: true
            });
        }
    }

    // ==========================================
    // TERMÔMETRO
    // ==========================================
    function updateThermometer(value) {
        const fill = document.getElementById('thermometer-fill');
        const valueDisplay = document.getElementById('temperature-value');
        if (!fill || !valueDisplay) return;
        
        const clampedValue = Math.max(0, Math.min(100, value));
        
        setTimeout(() => {
            fill.style.height = clampedValue + '%';
        }, 10);
        
        valueDisplay.textContent = Math.round(clampedValue) + '%';
        
        if (clampedValue >= 70) {
            fill.style.background = 'linear-gradient(to top, #10b981, #059669)';
            valueDisplay.style.background = '#10b981';
        } else if (clampedValue >= 40) {
            fill.style.background = 'linear-gradient(to top, #f59e0b, #d97706)';
            valueDisplay.style.background = '#f59e0b';
        } else {
            fill.style.background = 'linear-gradient(to top, #ef4444, #dc2626)';
            valueDisplay.style.background = '#ef4444';
        }
    }

    // ==========================================
    // ESTATÍSTICAS
    // ==========================================
    function updateStats(data) {
        const totalEl = document.getElementById('total-mentions');
        const positiveEl = document.getElementById('positive-mentions');
        const negativeEl = document.getElementById('negative-mentions');

        if (totalEl) totalEl.textContent = data.totalMentions.toLocaleString('pt-BR');
        if (positiveEl) positiveEl.textContent = data.positiveMentions.toLocaleString('pt-BR');
        if (negativeEl) negativeEl.textContent = data.negativeMentions.toLocaleString('pt-BR');
    }

    // ==========================================
    // RENDERIZAR MENÇÕES
    // ==========================================
    function renderMentions(mentions) {
        const container = document.getElementById('mentions');
        if (!container) return;

        if (!mentions || mentions.length === 0) {
            container.innerHTML = '<div class="loading" style="height: 100px;"><i class="fas fa-inbox"></i> Nenhuma menção encontrada.</div>';
            return;
        }

        const html = mentions.slice(0, 50).map(m => {
            const date = m.timestamp_utc ? 
                new Date(m.timestamp_utc).toLocaleDateString('pt-BR', { timeZone: 'UTC' }) : 
                'Data não disponível';
            
            const sentiment = (m.sentiment || 'NEUTRO').toUpperCase().trim();
            const sentimentClass = sentiment === 'POSITIVO' ? 'positive' : 
                                 sentiment === 'NEGATIVO' ? 'negative' : 'neutral';

            return `
                <div class="mention-item ${sentimentClass}-item">
                    <a href="${m.url || '#'}" target="_blank" rel="noopener noreferrer">
                        ${m.text || m.title || 'Texto não disponível'}
                    </a>
                    <div class="mention-source-main">
                        <i class="fas fa-database"></i> <strong>Fonte:</strong> ${m.source_platform || 'Não especificada'}
                    </div>
                    <div class="mention-meta">
                        <span class="mention-date"><i class="fas fa-calendar-alt"></i> ${date}</span>
                        <span class="mention-theme">${m.theme || 'Sem tema'}</span>
                        <span class="mention-sentiment ${sentimentClass}">${sentiment}</span>
                        ${m.location ? `<span class="mention-location"><i class="fas fa-map-marker-alt"></i> ${m.location}</span>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
        if (mentions.length > 50) {
            container.innerHTML += '<p class="loading" style="font-size: 0.9rem;">Mostrando as 50 mais recentes...</p>';
        }
    }

    // ==========================================
    // FETCH DATA
    // ==========================================
    async function fetchData(endpoint, params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const url = `${API_BASE_URL}/${endpoint}${queryString ? '?' + queryString : ''}`;
            
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            return await response.json();
        } catch (error) {
            console.error(`❌ Erro em ${endpoint}:`, error.message);
            return null;
        }
    }

    // ==========================================
    // CARREGAR GEOJSON
    // ==========================================
    async function loadGeojson() {
        try {
            console.log(`📥 Carregando: ${GEOJSON_PATH}`);
            const response = await fetch(GEOJSON_PATH);
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            
            if (data.type !== 'FeatureCollection') {
                throw new Error('GeoJSON inválido');
            }
            
            console.log(`✅ ${data.features.length} cidades carregadas`);
            return data;
            
        } catch (error) {
            console.error('❌ Erro ao carregar GeoJSON:', error);
            showError('Não foi possível carregar ma_cities.geojson', error.message);
            return null;
        }
    }

    // ==========================================
    // FILTROS E RENDERIZAÇÃO
    // ==========================================
    async function applyFiltersAndRender() {
        const theme = document.getElementById('theme-select')?.value || 'Todos';
        const search = document.getElementById('search-box')?.value || '';
        
        let title = "Visão Geral do Maranhão";
        const params = { limit: 100 };

        if (theme !== "Todos") {
            params.theme = theme;
            title = `Tema: ${theme}`;
        }

        if (search.trim()) {
            const normalized = search.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            const city = cityNames.find(n => 
                n.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "") === normalized
            );
            
            if (city) {
                params.location = city;
                title = `Detalhes de ${city}`;
                zoomToCity(city);
            } else {
                params.search_text = search;
                title += ` | Pesquisa: "${search}"`;
                zoomToCity("Maranhão");
            }
        } else {
            zoomToCity("Maranhão");
        }

        const container = document.getElementById('mentions');
        if (container) {
            container.innerHTML = '<div class="loading pulse"><i class="fas fa-spinner fa-spin"></i> Carregando...</div>';
        }

        allMentionsData = await fetchData('data', params) || [];
        renderMentions(allMentionsData);
        
        let positive = 0, negative = 0;
        allMentionsData.forEach(m => {
            const s = (m.sentiment || '').toUpperCase().trim();
            if (s === 'POSITIVO') positive++;
            else if (s === 'NEGATIVO') negative++;
        });
        
        updateStats({
            totalMentions: allMentionsData.length,
            positiveMentions: positive,
            negativeMentions: negative
        });
        
        const satisfaction = calculateSatisfaction(allMentionsData);
        updateThermometer(satisfaction);
        
        const titleEl = document.getElementById('details-title');
        if (titleEl) titleEl.textContent = title;
    }

    // ==========================================
    // CALCULAR SATISFAÇÃO
    // ==========================================
    function calculateSatisfaction(mentions) {
        if (!mentions || mentions.length === 0) return 50;
        
        let pos = 0, neg = 0;
        mentions.forEach(m => {
            const s = (m.sentiment || '').toUpperCase().trim();
            if (s === 'POSITIVO') pos++;
            else if (s === 'NEGATIVO') neg++;
        });
        
        const total = pos + neg;
        return total === 0 ? 50 : Math.round((pos / total) * 100);
    }

    // ==========================================
    // SUGESTÕES
    // ==========================================
    function setupSearchSuggestions() {
        const list = document.getElementById('suggestions');
        if (!list || !cityNames) return;

        list.innerHTML = '';
        [...cityNames].sort().forEach(name => {
            const opt = document.createElement('option');
            opt.value = name;
            list.appendChild(opt);
        });

        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            Array.from(themeSelect.options).forEach(opt => {
                if (opt.value !== "Todos") {
                    const o = document.createElement('option');
                    o.value = opt.value;
                    list.appendChild(o);
                }
            });
        }
    }

    // ==========================================
    // EVENT LISTENERS
    // ==========================================
    function setupEventListeners() {
        let timeout;
        const searchBox = document.getElementById('search-box');
        if (searchBox) {
            searchBox.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(applyFiltersAndRender, 500);
            });
        }

        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.addEventListener('change', applyFiltersAndRender);
        }
    }

    // ==========================================
    // ERRO
    // ==========================================
    function showError(message, details = null) {
        if (geojsonData !== null) return;
        
        const container = document.getElementById('details');
        if (container) {
            container.innerHTML = `
                <div class="error-message" style="text-align: center; padding: 2rem; color: #ef4444;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <h2>Erro ao Carregar</h2>
                    <p>${message}</p>
                    ${details ? `<pre style="background: #fff0f0; padding: 1rem; border-radius: 4px; margin-top: 0.5rem;">${details}</pre>` : ''}
                </div>
            `;
        }
    }

    // ==========================================
    // INICIALIZAÇÃO
    // ==========================================
    async function initializeDashboard() {
        try {
            console.log('🚀 Iniciando dashboard...');
            
            console.log('📍 1/5: Criando mapa...');
            initMap();
            
            console.log('📍 2/5: Carregando GeoJSON...');
            const geoData = await loadGeojson();
            if (!geoData) {
                console.error("❌ Falha crítica");
                return;
            }

            console.log('📍 3/5: Processando dados...');
            geojsonData = geoData;
            cityNames = geojsonData.features.map(f => f.properties.name).filter(Boolean);
            console.log(`✅ ${cityNames.length} cidades`);
            
            // Exporta para o sistema de busca
            window.cityNames = cityNames;
            console.log("✅ Lista de cidades exportada para window.cityNames");
            
            // Exporta a função de filtros para o sistema de busca
            window.applyFiltersAndRender = applyFiltersAndRender;
            console.log("✅ Função applyFiltersAndRender exportada para window");
            
            console.log('📍 4/5: Renderizando mapa...');
            await renderMapScores();
            
            console.log('📍 5/5: Configurando UI...');
            setupSearchSuggestions();
            setupEventListeners();
            await applyFiltersAndRender();

            console.log('🎉 DASHBOARD PRONTO!');

        } catch (error) {
            console.error('❌ ERRO FATAL:', error);
            showError('Erro fatal', error.stack);
        }
    }

    console.log('📄 Iniciando aplicação...');
    await initializeDashboard();
});

// ============================================
    // SISTEMA DE BUSCA MODERNO
    // ============================================
    function initModernSearch() {
        const searchBox = document.getElementById('search-box');
        if (!searchBox) return;

        // Remove o datalist antigo
        const oldDatalist = document.getElementById('suggestions');
        if (oldDatalist) {
            oldDatalist.style.display = 'none';
        }

        // Cria os elementos do novo sistema
        const searchContainer = searchBox.parentElement;
        searchContainer.classList.add('search-container');
        
        // Adiciona botão de limpar
        const clearBtn = document.createElement('button');
        clearBtn.className = 'clear-search-button';
        clearBtn.innerHTML = '<i class="fas fa-times"></i>';
        clearBtn.id = 'clear-search-btn';
        searchContainer.appendChild(clearBtn);

        // Adiciona dropdown de sugestões
        const dropdown = document.createElement('div');
        dropdown.className = 'search-suggestions-dropdown';
        dropdown.id = 'search-suggestions-dropdown';
        searchContainer.appendChild(dropdown);

        let selectedIndex = -1;
        let searchTimeout;

        // Mostra/esconde botão de limpar
        searchBox.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            if (this.value.length > 0) {
                clearBtn.classList.add('active');
                
                // Debounce para não buscar a cada tecla
                searchTimeout = setTimeout(() => {
                    mostrarSugestoes(this.value);
                }, 200);
            } else {
                clearBtn.classList.remove('active');
                dropdown.classList.remove('active');
            }
        });

        // Limpar campo
        clearBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            searchBox.value = '';
            searchBox.focus();
            clearBtn.classList.remove('active');
            dropdown.classList.remove('active');
            
            // Aplica filtros vazios (mostra tudo)
            if (typeof applyFiltersAndRender === 'function') {
                applyFiltersAndRender();
            }
        });

        // Função para mostrar sugestões
        function mostrarSugestoes(query) {
            const lowerQuery = query.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            
            // Filtra cidades
            const cidadesFiltradas = (cityNames || []).filter(cidade => 
                cidade.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").includes(lowerQuery)
            ).slice(0, 8);

            // Filtra temas
            const temasDisponiveis = [
                { nome: 'Segurança', icon: 'shield-alt' },
                { nome: 'Infraestrutura', icon: 'road' },
                { nome: 'Comércio', icon: 'store' },
                { nome: 'Saúde', icon: 'heartbeat' },
                { nome: 'Educação', icon: 'graduation-cap' },
                { nome: 'Transporte', icon: 'bus' }
            ];

            const temasFiltrados = temasDisponiveis.filter(tema =>
                tema.nome.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").includes(lowerQuery)
            );

            // Monta HTML
            let html = '';

            if (cidadesFiltradas.length > 0) {
                html += `<div class="search-suggestion-group">
                    <div class="search-suggestion-group-title">📍 Cidades</div>`;
                
                cidadesFiltradas.forEach(cidade => {
                    html += `
                        <div class="search-suggestion-item" data-type="cidade" data-value="${cidade}">
                            <div class="search-suggestion-icon">
                                <i class="fas fa-map-marker-alt"></i>
                            </div>
                            <div class="search-suggestion-content">
                                <div class="search-suggestion-name">${cidade}</div>
                                <div class="search-suggestion-meta">Maranhão</div>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
            }

            if (temasFiltrados.length > 0) {
                html += `<div class="search-suggestion-group">
                    <div class="search-suggestion-group-title">🏷️ Temas</div>`;
                
                temasFiltrados.forEach(tema => {
                    html += `
                        <div class="search-suggestion-item" data-type="tema" data-value="${tema.nome}">
                            <div class="search-suggestion-icon">
                                <i class="fas fa-${tema.icon}"></i>
                            </div>
                            <div class="search-suggestion-content">
                                <div class="search-suggestion-name">${tema.nome}</div>
                                <div class="search-suggestion-meta">Tema</div>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
            }

            // Se não houver resultados
            if (html === '') {
                html = `
                    <div class="search-no-results">
                        <i class="fas fa-search"></i>
                        <div>Nenhum resultado encontrado</div>
                    </div>
                `;
            }

            dropdown.innerHTML = html;
            dropdown.classList.add('active');
            selectedIndex = -1;

            // Adiciona event listeners aos itens
            dropdown.querySelectorAll('.search-suggestion-item').forEach(item => {
                item.addEventListener('click', function() {
                    selecionarItem(this);
                });
            });
        }

        // Selecionar item
        function selecionarItem(element) {
            const value = element.dataset.value;
            
            searchBox.value = value;
            dropdown.classList.remove('active');
            clearBtn.classList.add('active');
            
            console.log(`✅ Selecionado: ${value}`);
            
            // Aplica os filtros
            if (typeof applyFiltersAndRender === 'function') {
                applyFiltersAndRender();
            }
        }

        // Navegação por teclado
        searchBox.addEventListener('keydown', function(e) {
            const items = dropdown.querySelectorAll('.search-suggestion-item');
            
            if (items.length === 0) return;

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIndex = (selectedIndex + 1) % items.length;
                atualizarSelecao(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIndex = selectedIndex <= 0 ? items.length - 1 : selectedIndex - 1;
                atualizarSelecao(items);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (selectedIndex >= 0 && items[selectedIndex]) {
                    selecionarItem(items[selectedIndex]);
                } else if (this.value.length > 0) {
                    dropdown.classList.remove('active');
                    if (typeof applyFiltersAndRender === 'function') {
                        applyFiltersAndRender();
                    }
                }
            } else if (e.key === 'Escape') {
                dropdown.classList.remove('active');
            }
        });

        function atualizarSelecao(items) {
            items.forEach((item, index) => {
                if (index === selectedIndex) {
                    item.classList.add('selected');
                    item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
                } else {
                    item.classList.remove('selected');
                }
            });
        }

        // Fecha dropdown ao clicar fora
        document.addEventListener('click', function(e) {
            if (!searchContainer.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });

        // Reabre dropdown ao focar no campo (se tiver texto)
        searchBox.addEventListener('focus', function() {
            if (this.value.length > 0) {
                mostrarSugestoes(this.value);
            }
        });

        console.log('✅ Sistema de busca moderno inicializado');
    }
      // Sistema de busca de CIDADES
        (function() {
            const searchBox = document.getElementById('search-box');
            const clearBtn = document.getElementById('search-clear');
            const dropdown = document.getElementById('city-dropdown');
            
            let searchTimeout;
            let cities = [];
            
            // Aguarda as cidades serem carregadas
            const waitForCities = setInterval(() => {
                if (window.cityNames && window.cityNames.length > 0) {
                    cities = window.cityNames;
                    clearInterval(waitForCities);
                    console.log('✅ Sistema de busca pronto:', cities.length, 'cidades');
                }
            }, 100);
            
            // Input com debounce
            searchBox.addEventListener('input', function() {
                const query = this.value.trim();
                
                clearTimeout(searchTimeout);
                
                if (query.length > 0) {
                    clearBtn.classList.add('show');
                    
                    searchTimeout = setTimeout(() => {
                        showCitySuggestions(query);
                    }, 200);
                } else {
                    clearBtn.classList.remove('show');
                    dropdown.classList.remove('show');
                }
            });
            
            // Focus no campo
            searchBox.addEventListener('focus', function() {
                if (this.value.trim().length > 0) {
                    showCitySuggestions(this.value.trim());
                }
            });
            
            // Click no campo (abre dropdown mesmo sem digitar)
            searchBox.addEventListener('click', function() {
                if (cities.length > 0 && this.value.trim().length === 0) {
                    showAllCities();
                }
            });
            
            // Botão limpar
            clearBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                searchBox.value = '';
                searchBox.focus();
                clearBtn.classList.remove('show');
                dropdown.classList.remove('show');
                
                if (typeof applyFiltersAndRender === 'function') {
                    applyFiltersAndRender();
                }
            });
            
            // Mostra todas as cidades (quando clicar no campo vazio)
            function showAllCities() {
                const sortedCities = [...cities].sort();
                // ✅ CORREÇÃO: Removido limite, mostra TODAS as cidades
                
                let html = '<div class="dropdown-header">';
                html += `<i class="fas fa-map-marker-alt"></i> ${sortedCities.length} Cidades do Maranhão`;
                html += '</div>';
                
                sortedCities.forEach(cidade => {
                    const cityEscaped = cidade.replace(/'/g, "\\'");
                    html += `
                        <div class="dropdown-item" data-city="${cityEscaped}">
                            <div class="dropdown-icon">
                                <i class="fas fa-map-marker-alt"></i>
                            </div>
                            <div class="dropdown-text">
                                <div class="dropdown-name">${cidade}</div>
                                <div class="dropdown-meta">Maranhão, Brasil</div>
                            </div>
                        </div>
                    `;
                });
                
                dropdown.innerHTML = html;
                dropdown.classList.add('show');
            }
            
            // Mostra sugestões filtradas
            function showCitySuggestions(query) {
                const lowerQuery = query.toLowerCase()
                    .normalize("NFD")
                    .replace(/[\u0300-\u036f]/g, "");
                
                const filtered = cities.filter(cidade => 
                    cidade.toLowerCase()
                        .normalize("NFD")
                        .replace(/[\u0300-\u036f]/g, "")
                        .includes(lowerQuery)
                );
                // ✅ CORREÇÃO: Removido limite, mostra TODAS as cidades filtradas
                
                if (filtered.length === 0) {
                    dropdown.innerHTML = `
                        <div class="no-results">
                            <i class="fas fa-search"></i>
                            <div>Nenhuma cidade encontrada</div>
                        </div>
                    `;
                    dropdown.classList.add('show');
                    return;
                }
                
                let html = '<div class="dropdown-header">';
                html += '<i class="fas fa-map-marker-alt"></i> ';
                html += filtered.length === 1 ? '1 Cidade' : `${filtered.length} Cidades`;
                html += '</div>';
                
                filtered.forEach(cidade => {
                    html += `
                        <div class="dropdown-item" onclick="selectCity('${cidade}')">
                            <div class="dropdown-icon">
                                <i class="fas fa-map-marker-alt"></i>
                            </div>
                            <div class="dropdown-text">
                                <div class="dropdown-name">${cidade}</div>
                                <div class="dropdown-meta">Maranhão, Brasil</div>
                            </div>
                        </div>
                    `;
                });
                
                dropdown.innerHTML = html;
                dropdown.classList.add('show');
            }
            
            // Função global para selecionar cidade
            window.selectCity = function(cityName) {
                searchBox.value = cityName;
                clearBtn.classList.add('show');
                
                console.log('🏙️ Cidade selecionada:', cityName);
                
                // Mantém o dropdown aberto com feedback visual
                let html = '<div class="dropdown-header" style="background: #eef2ff; color: #4f46e5;">';
                html += '<i class="fas fa-check-circle"></i> Cidade Selecionada';
                html += '</div>';
                
                html += `
                    <div class="dropdown-item" style="background: #eef2ff; border-left: 4px solid #4f46e5;">
                        <div class="dropdown-icon" style="background: #4f46e5; color: white;">
                            <i class="fas fa-map-marker-alt"></i>
                        </div>
                        <div class="dropdown-text">
                            <div class="dropdown-name" style="color: #4f46e5;">${cityName}</div>
                            <div class="dropdown-meta" style="color: #6b7280;">
                                <i class="fas fa-check"></i> Buscando dados...
                            </div>
                        </div>
                    </div>
                `;
                
                dropdown.innerHTML = html;
                dropdown.classList.add('show');
                
                // Fecha o dropdown após 2 segundos
                setTimeout(() => {
                    dropdown.classList.remove('show');
                }, 2000);
                
                if (typeof applyFiltersAndRender === 'function') {
                    applyFiltersAndRender();
                }
            };
            
            // Fecha dropdown ao clicar fora
            document.addEventListener('click', function(e) {
                if (!searchBox.contains(e.target) && !dropdown.contains(e.target)) {
                    dropdown.classList.remove('show');
                }
            });
            
            // Teclas Enter e Esc
            searchBox.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    dropdown.classList.remove('show');
                    if (typeof applyFiltersAndRender === 'function') {
                        applyFiltersAndRender();
                    }
                } else if (e.key === 'Escape') {
                    dropdown.classList.remove('show');
                }
            });
        })();

// Sistema de busca de CIDADES
        (function() {
            const searchBox = document.getElementById('search-box');
            const clearBtn = document.getElementById('search-clear');
            const dropdown = document.getElementById('city-dropdown');
            
            let searchTimeout;
            let cities = [];
            
            // Aguarda as cidades serem carregadas
            const waitForCities = setInterval(() => {
                if (window.cityNames && window.cityNames.length > 0) {
                    cities = window.cityNames;
                    clearInterval(waitForCities);
                    console.log('✅ Sistema de busca pronto:', cities.length, 'cidades');
                }
            }, 100);
            
            // Input com debounce
            searchBox.addEventListener('input', function() {
                const query = this.value.trim();
                
                clearTimeout(searchTimeout);
                
                if (query.length > 0) {
                    clearBtn.classList.add('show');
                    
                    searchTimeout = setTimeout(() => {
                        showCitySuggestions(query);
                    }, 200);
                } else {
                    clearBtn.classList.remove('show');
                    dropdown.classList.remove('show');
                }
            });
            
            // Focus no campo
            searchBox.addEventListener('focus', function() {
                if (this.value.trim().length > 0) {
                    showCitySuggestions(this.value.trim());
                }
            });
            
            // Click no campo (abre dropdown mesmo sem digitar)
            searchBox.addEventListener('click', function() {
                if (cities.length > 0 && this.value.trim().length === 0) {
                    showAllCities();
                }
            });
            
            // Botão limpar
            clearBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                searchBox.value = '';
                searchBox.focus();
                clearBtn.classList.remove('show');
                dropdown.classList.remove('show');
                
                if (typeof applyFiltersAndRender === 'function') {
                    applyFiltersAndRender();
                }
            });
            
            // Mostra todas as cidades (quando clicar no campo vazio)
            function showAllCities() {
                const sortedCities = [...cities].sort();
                // ✅ CORREÇÃO: Removido limite, mostra TODAS as cidades
                
                let html = '<div class="dropdown-header">';
                html += `<i class="fas fa-map-marker-alt"></i> ${sortedCities.length} Cidades do Maranhão`;
                html += '</div>';
                
                sortedCities.forEach(cidade => {
                    const cityEscaped = cidade.replace(/'/g, "\\'");
                    html += `
                        <div class="dropdown-item" onclick="selectCity('${cityEscaped}')">
                            <div class="dropdown-icon">
                                <i class="fas fa-map-marker-alt"></i>
                            </div>
                            <div class="dropdown-text">
                                <div class="dropdown-name">${cidade}</div>
                                <div class="dropdown-meta">Maranhão, Brasil</div>
                            </div>
                        </div>
                    `;
                });
                
                dropdown.innerHTML = html;
                dropdown.classList.add('show');
            }
            
            // Mostra sugestões filtradas
            function showCitySuggestions(query) {
                const lowerQuery = query.toLowerCase()
                    .normalize("NFD")
                    .replace(/[\u0300-\u036f]/g, "");
                
                const filtered = cities.filter(cidade => 
                    cidade.toLowerCase()
                        .normalize("NFD")
                        .replace(/[\u0300-\u036f]/g, "")
                        .includes(lowerQuery)
                );
                // ✅ CORREÇÃO: Removido limite, mostra TODAS as cidades filtradas
                
                if (filtered.length === 0) {
                    dropdown.innerHTML = `
                        <div class="no-results">
                            <i class="fas fa-search"></i>
                            <div>Nenhuma cidade encontrada</div>
                        </div>
                    `;
                    dropdown.classList.add('show');
                    return;
                }
                
                let html = '<div class="dropdown-header">';
                html += '<i class="fas fa-map-marker-alt"></i> ';
                html += filtered.length === 1 ? '1 Cidade' : `${filtered.length} Cidades`;
                html += '</div>';
                
                filtered.forEach(cidade => {
                    const cityEscaped = cidade.replace(/'/g, "\\'");
                    html += `
                        <div class="dropdown-item" onclick="selectCity('${cityEscaped}')">
                            <div class="dropdown-icon">
                                <i class="fas fa-map-marker-alt"></i>
                            </div>
                            <div class="dropdown-text">
                                <div class="dropdown-name">${cidade}</div>
                                <div class="dropdown-meta">Maranhão, Brasil</div>
                            </div>
                        </div>
                    `;
                });
                
                dropdown.innerHTML = html;
                dropdown.classList.add('show');
            }
            
            // Função global para selecionar cidade - COM FEEDBACK VISUAL
            window.selectCity = function(cityName) {
                searchBox.value = cityName;
                clearBtn.classList.add('show');
                
                console.log('🏙️ Cidade selecionada:', cityName);
                
                // Mantém o dropdown aberto com feedback visual
                let html = '<div class="dropdown-header" style="background: #eef2ff; color: #4f46e5;">';
                html += '<i class="fas fa-check-circle"></i> Cidade Selecionada';
                html += '</div>';
                
                html += `
                    <div class="dropdown-item" style="background: #eef2ff; border-left: 4px solid #4f46e5;">
                        <div class="dropdown-icon" style="background: #4f46e5; color: white;">
                            <i class="fas fa-map-marker-alt"></i>
                        </div>
                        <div class="dropdown-text">
                            <div class="dropdown-name" style="color: #4f46e5;">${cityName}</div>
                            <div class="dropdown-meta" style="color: #6b7280;">
                                <i class="fas fa-check"></i> Buscando dados...
                            </div>
                        </div>
                    </div>
                `;
                
                dropdown.innerHTML = html;
                dropdown.classList.add('show');
                
                // Fecha o dropdown após 2 segundos
                setTimeout(() => {
                    dropdown.classList.remove('show');
                }, 2000);
                
                if (typeof applyFiltersAndRender === 'function') {
                    applyFiltersAndRender();
                }
            };
            
            // Fecha dropdown ao clicar fora
            document.addEventListener('click', function(e) {
                if (!searchBox.contains(e.target) && !dropdown.contains(e.target)) {
                    dropdown.classList.remove('show');
                }
            });
            
            // Teclas Enter e Esc
            searchBox.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    dropdown.classList.remove('show');
                    if (typeof applyFiltersAndRender === 'function') {
                        applyFiltersAndRender();
                    }
                } else if (e.key === 'Escape') {
                    dropdown.classList.remove('show');
                }
            });
        })();
        
        // ==========================================
        // SISTEMA DE DROPDOWN DE TEMAS CUSTOMIZADO
        // ==========================================
        (function() {
            const themeDisplay = document.getElementById('theme-display');
            const themeSelect = document.getElementById('theme-select');
            const themeDropdown = document.getElementById('theme-dropdown');
            const themeChevron = document.getElementById('theme-chevron');
            
            const themes = [
                { value: 'Todos', label: 'Todos os Temas', icon: 'fas fa-th' },
                { value: 'Segurança', label: 'Segurança', icon: 'fas fa-shield-alt' },
                { value: 'Infraestrutura', label: 'Infraestrutura', icon: 'fas fa-road' },
                { value: 'Comércio', label: 'Comércio', icon: 'fas fa-store' },
                { value: 'Saúde', label: 'Saúde', icon: 'fas fa-heartbeat' },
                { value: 'Educação', label: 'Educação', icon: 'fas fa-graduation-cap' },
                { value: 'Transporte', label: 'Transporte', icon: 'fas fa-bus' }
            ];
            
            // Abre/fecha dropdown ao clicar no campo
            themeDisplay.addEventListener('click', function(e) {
                e.stopPropagation();
                const isOpen = themeDropdown.classList.contains('show');
                
                if (isOpen) {
                    themeDropdown.classList.remove('show');
                    themeChevron.style.transform = 'translateY(-50%)';
                } else {
                    showThemeOptions();
                    themeChevron.style.transform = 'translateY(-50%) rotate(180deg)';
                }
            });
            
            // Mostra todas as opções de temas
            function showThemeOptions() {
                let html = '<div class="dropdown-header">';
                html += '<i class="fas fa-filter"></i> Selecione um Tema';
                html += '</div>';
                
                themes.forEach(theme => {
                    const isSelected = themeSelect.value === theme.value;
                    const selectedStyle = isSelected ? 'background: #eef2ff; border-left: 4px solid #4f46e5;' : '';
                    
                    html += `
                        <div class="dropdown-item" onclick="selectTheme('${theme.value}', '${theme.label}')" style="${selectedStyle}">
                            <div class="dropdown-icon" style="${isSelected ? 'background: #4f46e5; color: white;' : ''}">
                                <i class="${theme.icon}"></i>
                            </div>
                            <div class="dropdown-text">
                                <div class="dropdown-name" style="${isSelected ? 'color: #4f46e5;' : ''}">${theme.label}</div>
                                ${isSelected ? '<div class="dropdown-meta" style="color: #4f46e5;"><i class="fas fa-check"></i> Selecionado</div>' : ''}
                            </div>
                        </div>
                    `;
                });
                
                themeDropdown.innerHTML = html;
                themeDropdown.classList.add('show');
            }
            
            // Função global para selecionar tema
            window.selectTheme = function(value, label) {
                themeDisplay.value = label;
                themeSelect.value = value;
                
                console.log('🎨 Tema selecionado:', label);
                
                // Mantém o dropdown aberto com feedback visual
                let html = '<div class="dropdown-header" style="background: #eef2ff; color: #4f46e5;">';
                html += '<i class="fas fa-check-circle"></i> Tema Aplicado';
                html += '</div>';
                
                const theme = themes.find(t => t.value === value);
                
                html += `
                    <div class="dropdown-item" style="background: #eef2ff; border-left: 4px solid #4f46e5;">
                        <div class="dropdown-icon" style="background: #4f46e5; color: white;">
                            <i class="${theme.icon}"></i>
                        </div>
                        <div class="dropdown-text">
                            <div class="dropdown-name" style="color: #4f46e5;">${label}</div>
                            <div class="dropdown-meta" style="color: #6b7280;">
                                <i class="fas fa-check"></i> Filtrando dados...
                            </div>
                        </div>
                    </div>
                `;
                
                themeDropdown.innerHTML = html;
                themeDropdown.classList.add('show');
                
                // Fecha o dropdown após 1.5 segundos
                setTimeout(() => {
                    themeDropdown.classList.remove('show');
                    themeChevron.style.transform = 'translateY(-50%)';
                }, 1500);
                
                // Chama a função de filtro
                if (typeof applyFiltersAndRender === 'function') {
                    applyFiltersAndRender();
                }
            };
            
            // Fecha dropdown ao clicar fora
            document.addEventListener('click', function(e) {
                if (!themeDisplay.contains(e.target) && !themeDropdown.contains(e.target)) {
                    themeDropdown.classList.remove('show');
                    themeChevron.style.transform = 'translateY(-50%)';
                }
            });
        })();