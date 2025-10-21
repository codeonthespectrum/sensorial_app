// API Base URL
const API_URL = 'http://localhost:8000';
let authToken = localStorage.getItem('authToken');
let currentUser = null;
let mapa = null;
let marcadorAtual = null;
let userLocation = null;

// ============= INICIALIZAÇÃO =============
document.addEventListener('DOMContentLoaded', () => {
    loadTiposAmbiente();
    carregarStats();
    setupEventListeners();
    
    if (authToken) {
        verificarAutenticacao();
    }
});

function setupEventListeners() {
    // Auth buttons
    document.getElementById('loginBtn').addEventListener('click', () => openModal('loginModal'));
    document.getElementById('registerBtn').addEventListener('click', () => openModal('registerModal'));
    document.getElementById('logoutBtn').addEventListener('click', fazerLogout);
    
    // Nav tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            switchTab(tabName);
        });
    });
    
    // Close modals on click outside
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// ============= AUTENTICAÇÃO =============
async function fazerRegistro() {
    const nome = document.getElementById('registerNome').value;
    const email = document.getElementById('registerEmail').value;
    const senha = document.getElementById('registerSenha').value;
    const cidade = document.getElementById('registerCidade').value;
    const neurodiversidade = document.getElementById('registerNeurodiversidade').value;
    
    if (!nome || !email || !senha || !cidade) {
        showNotification('Preencha todos os campos', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/registro`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nome,
                email,
                senha,
                cidade,
                neurodiversidade
            })
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Erro ao registrar');
        }
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        
        closeModal('registerModal');
        showNotification('✅ Registrado com sucesso!');
        verificarAutenticacao();
        carregarStats();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function fazerLogin() {
    const email = document.getElementById('loginEmail').value;
    const senha = document.getElementById('loginSenha').value;
    
    if (!email || !senha) {
        showNotification('Preencha email e senha', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, senha })
        });
        
        if (!response.ok) {
            throw new Error('Email ou senha inválidos');
        }
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        
        closeModal('loginModal');
        showNotification('✅ Login realizado!');
        verificarAutenticacao();
        carregarStats();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

function fazerLogout() {
    authToken = null;
    localStorage.removeItem('authToken');
    currentUser = null;
    
    // Reset UI
    document.getElementById('loginBtn').style.display = 'block';
    document.getElementById('registerBtn').style.display = 'block';
    document.getElementById('logoutBtn').style.display = 'none';
    
    // Hide perfil tab
    document.querySelectorAll('.nav-tab')[3].style.display = 'none';
    
    switchTab('inicio');
    showNotification('✅ Desconectado!');
    carregarStats();
}

async function verificarAutenticacao() {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            
            // Update UI
            document.getElementById('loginBtn').style.display = 'none';
            document.getElementById('registerBtn').style.display = 'none';
            document.getElementById('logoutBtn').style.display = 'block';
            
            // Show perfil tab
            document.querySelectorAll('.nav-tab')[3].style.display = 'block';
            
            carregarPerfil();
        } else {
            throw new Error('Token inválido');
        }
    } catch (error) {
        authToken = null;
        localStorage.removeItem('authToken');
        console.error(error);
    }
}

// ============= CARREGAMENTO DE DADOS =============
async function carregarStats() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        
        document.getElementById('statsUsers').textContent = data.usuarios_cadastrados;
        document.getElementById('statsLocais').textContent = data.locais_cadastrados;
        document.getElementById('statsRegistros').textContent = data.registros_totais;
    } catch (error) {
        console.error(error);
    }
}

async function loadTiposAmbiente() {
    try {
        const response = await fetch(`${API_URL}/tipos-ambiente`);
        const data = await response.json();
        
        const tipos = data.tipos;
        
        // Preencher ambos os selects
        [document.getElementById('tipoAmbiente'), document.getElementById('tipoAmbienteFilter')].forEach(select => {
            tipos.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo.valor;
                option.textContent = tipo.valor;
                if (select.id !== 'tipoAmbienteFilter') {
                    select.appendChild(option);
                } else {
                    if (tipos.indexOf(tipo) === 0) return;
                    select.appendChild(option);
                }
            });
        });
        
        // Preencher o filter select
        const filterSelect = document.getElementById('tipoAmbienteFilter');
        tipos.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.valor;
            option.textContent = tipo.valor;
            filterSelect.appendChild(option);
        });
    } catch (error) {
        console.error(error);
    }
}

async function buscarLocais() {
    const tipoAmbiente = document.getElementById('tipoAmbienteFilter').value;
    const searchText = document.getElementById('searchLocal').value.toLowerCase();
    
    try {
        // Usar localização do usuário ou padrão
        const lat = userLocation ? userLocation.lat : -23.5505;
        const lng = userLocation ? userLocation.lng : -46.6333;
        
        let url = `${API_URL}/locais/proximos?latitude=${lat}&longitude=${lng}`;
        
        if (tipoAmbiente) {
            url += `&tipo_ambiente=${tipoAmbiente}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        // Filtrar por texto
        let locaisFiltrados = data.locais;
        if (searchText) {
            locaisFiltrados = locaisFiltrados.filter(local => 
                local.nome_local.toLowerCase().includes(searchText) ||
                (local.endereco ? local.endereco.toLowerCase().includes(searchText) : false)
            );
        }
        
        const locaisList = document.getElementById('locaisList');
        
        if (locaisFiltrados.length === 0) {
            locaisList.innerHTML = '<p class="empty">Nenhum local encontrado</p>';
            // Limpar mapa
            if (mapa) {
                mapa.eachLayer((layer) => {
                    if (layer instanceof L.Marker) {
                        mapa.removeLayer(layer);
                    }
                });
            }
            return;
        }
        
        // Renderizar cards
        locaisList.innerHTML = locaisFiltrados.map(local => `
            <div class="local-card" onclick="carregarDetalhesLocal('${local.place_id}')">
                <h3>${local.nome_local}</h3>
                <span class="type-badge">${local.tipo_ambiente}</span>
                ${local.selo_acessivel ? '<span class="seal">✅ Selo Acessível</span>' : ''}
                
                <div class="local-metrics">
                    <div class="metric">
                        <div class="metric-label">Ruído</div>
                        <div class="metric-value">
                            <span class="nivel-badge nivel-${local.nivel_ruido_atual}">${local.nivel_ruido_atual}</span>
                        </div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Luz</div>
                        <div class="metric-value">
                            <span class="nivel-badge nivel-${local.nivel_luz_atual}">${local.nivel_luz_atual}</span>
                        </div>
                    </div>
                </div>
                
                <p><strong>Última atualização:</strong> ${formatarData(local.ultima_atualizacao)}</p>
            </div>
        `).join('');
        
        // Adicionar marcadores no mapa
        if (mapa) {
            // Limpar marcadores anteriores
            mapa.eachLayer((layer) => {
                if (layer instanceof L.Marker) {
                    mapa.removeLayer(layer);
                }
            });
            
            // Adicionar novos marcadores
            locaisFiltrados.forEach(local => {
                const color = local.nivel_ruido_atual === 'Bom' ? 'green' : 
                             local.nivel_ruido_atual === 'Ok' ? 'orange' : 'red';
                
                L.circleMarker([local.coordenadas.latitude, local.coordenadas.longitude], {
                    radius: 10,
                    fillColor: color,
                    color: color,
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                })
                .bindPopup(`<strong>${local.nome_local}</strong><br/>${local.tipo_ambiente}`)
                .addTo(mapa);
            });
            
            // Centralizar mapa
            if (locaisFiltrados.length > 0) {
                const bounds = L.latLngBounds(locaisFiltrados.map(l => [l.coordenadas.latitude, l.coordenadas.longitude]));
                mapa.fitBounds(bounds, { padding: [50, 50] });
            }
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function carregarDetalhesLocal(placeId) {
    try {
        const response = await fetch(`${API_URL}/locais/${placeId}`);
        if (!response.ok) throw new Error('Local não encontrado');
        
        const local = await response.json();
        
        document.getElementById('detailsTitle').textContent = local.nome_local;
        
        let html = `
            <div class="detail-grid">
                <div class="detail-item">
                    <label>Endereço</label>
                    <p>${local.endereco}</p>
                </div>
                <div class="detail-item">
                    <label>Tipo</label>
                    <p>${local.tipo_ambiente}</p>
                </div>
                <div class="detail-item">
                    <label>Coordenadas</label>
                    <p>${local.coordenadas.latitude.toFixed(4)}, ${local.coordenadas.longitude.toFixed(4)}</p>
                </div>
                <div class="detail-item">
                    <label>Total de Registros</label>
                    <p>${local.total_registros}</p>
                </div>
                <div class="detail-item">
                    <label>Ruído Atual</label>
                    <p><span class="nivel-badge nivel-${local.nivel_ruido_atual}">${local.nivel_ruido_atual}</span></p>
                </div>
                <div class="detail-item">
                    <label>Luz Atual</label>
                    <p><span class="nivel-badge nivel-${local.nivel_luz_atual}">${local.nivel_luz_atual}</span></p>
                </div>
            </div>
        `;
        
        if (local.selo_acessivel) {
            html += '<p style="color: var(--success); font-weight: bold;">✅ Este local tem Selo Acessível!</p>';
        }
        
        if (local.ultimos_5_registros && local.ultimos_5_registros.length > 0) {
            html += `
                <h3>Últimos Registros</h3>
                <table class="registros-table">
                    <thead>
                        <tr>
                            <th>Data/Hora</th>
                            <th>Ruído</th>
                            <th>Luz</th>
                            <th>dB</th>
                            <th>Lux</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${local.ultimos_5_registros.map(reg => `
                            <tr>
                                <td>${formatarData(reg.timestamp)}</td>
                                <td><span class="nivel-badge nivel-${reg.nivel_ruido}">${reg.nivel_ruido}</span></td>
                                <td><span class="nivel-badge nivel-${reg.nivel_luz}">${reg.nivel_luz}</span></td>
                                <td>${reg.ruido_db ? reg.ruido_db.toFixed(1) : '-'}</td>
                                <td>${reg.luminosidade_lux ? reg.luminosidade_lux.toFixed(1) : '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
        
        document.getElementById('detailsContent').innerHTML = html;
        openModal('localDetailsModal');
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function carregarPerfil() {
    if (!currentUser) return;
    
    const html = `
        <div class="perfil-item">
            <label>Nome</label>
            <p>${currentUser.nome}</p>
        </div>
        <div class="perfil-item">
            <label>Email</label>
            <p>${currentUser.email}</p>
        </div>
        <div class="perfil-item">
            <label>Cidade</label>
            <p>${currentUser.cidade}</p>
        </div>
        <div class="perfil-item">
            <label>Neurodiversidade</label>
            <p>${currentUser.neurodiversidade === 'Nao Informado' ? 'Não informado' : currentUser.neurodiversidade}</p>
        </div>
    `;
    
    document.getElementById('perfilContent').innerHTML = html;
}

// ============= REGISTROS =============
async function enviarRegistroManual() {
    if (!authToken) {
        showNotification('Você precisa estar autenticado', 'error');
        return;
    }
    
    const nomeLocal = document.getElementById('nomeLocal').value;
    const endereco = document.getElementById('endereco').value;
    const tipoAmbiente = document.getElementById('tipoAmbiente').value;
    const latitude = parseFloat(document.getElementById('latitude').value);
    const longitude = parseFloat(document.getElementById('longitude').value);
    const nivelRuido = document.getElementById('nivelRuidoManual').value;
    const nivelLuz = document.getElementById('nivelLuzManual').value;
    
    if (!nomeLocal || !endereco || !tipoAmbiente || !latitude || !longitude) {
        showNotification('Preencha todos os campos obrigatórios', 'error');
        return;
    }
    
    if (!nivelRuido || !nivelLuz) {
        showNotification('Selecione os níveis de ruído e luz', 'error');
        return;
    }
    
    const body = {
        place_id: `${nomeLocal.replace(/\s+/g, '_')}_${Date.now()}`,
        nome_local: nomeLocal,
        endereco: endereco,
        tipo_ambiente: tipoAmbiente,
        coordenadas: {
            latitude: latitude,
            longitude: longitude
        },
        nivel_ruido_manual: nivelRuido,
        nivel_luz_manual: nivelLuz
    };
    
    try {
        const response = await fetch(`${API_URL}/registros`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(body)
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Erro ao criar registro');
        }
        
        const data = await response.json();
        showNotification('✅ Classificação salva com sucesso!');
        
        // Limpar formulário
        document.getElementById('nomeLocal').value = '';
        document.getElementById('endereco').value = '';
        document.getElementById('tipoAmbiente').value = '';
        document.getElementById('latitude').value = '';
        document.getElementById('longitude').value = '';
        document.getElementById('nivelRuidoManual').value = '';
        document.getElementById('nivelLuzManual').value = '';
        document.getElementById('geoStatus').textContent = '';
        
        carregarStats();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// ============= UTILITÁRIOS =============
// ============= GEOLOCALIZAÇÃO =============

async function obterGeolocalizacao() {
    const statusEl = document.getElementById('geoStatus');
    
    if (!navigator.geolocation) {
        statusEl.textContent = '❌ Geolocalização não suportada neste navegador';
        statusEl.style.color = 'var(--danger)';
        return;
    }
    
    statusEl.textContent = '📍 Obtendo localização...';
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const { latitude, longitude } = position.coords;
            
            document.getElementById('latitude').value = latitude.toFixed(6);
            document.getElementById('longitude').value = longitude.toFixed(6);
            userLocation = { lat: latitude, lng: longitude };
            
            statusEl.textContent = `✅ Localização obtida! (${latitude.toFixed(4)}, ${longitude.toFixed(4)})`;
            statusEl.style.color = 'var(--success)';
            
            // Obter nome do endereço via Nominatim (OpenStreetMap)
            fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`)
                .then(r => r.json())
                .then(data => {
                    if (data.address) {
                        const endereço = data.address.road ? `${data.address.road}, ${data.address.house_number || ''}` : 
                                        data.address.street ? data.address.street : 
                                        data.address.neighbourhood ? data.address.neighbourhood : 
                                        data.display_name.split(',')[0];
                        document.getElementById('endereco').value = endereço.trim();
                    }
                })
                .catch(err => console.log('Erro ao obter endereço:', err));
        },
        (error) => {
            if (error.code === error.PERMISSION_DENIED) {
                statusEl.textContent = '❌ Permissão de localização negada. Habilite nos settings do seu celular.';
            } else if (error.code === error.POSITION_UNAVAILABLE) {
                statusEl.textContent = '❌ Localização não disponível neste momento';
            } else {
                statusEl.textContent = `❌ Erro: ${error.message}`;
            }
            statusEl.style.color = 'var(--danger)';
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

async function usarGeolocalizacao() {
    if (!navigator.geolocation) {
        showNotification('Geolocalização não suportada', 'error');
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const { latitude, longitude } = position.coords;
            userLocation = { lat: latitude, lng: longitude };
            
            // Inicializar mapa se não existir
            if (!mapa) {
                inicializarMapa(latitude, longitude);
            } else {
                mapa.setView([latitude, longitude], 15);
            }
            
            buscarLocais();
            showNotification('📍 Usando sua localização atual');
        },
        (error) => {
            showNotification('Permissão de localização negada', 'error');
        }
    );
}

function inicializarMapa(lat = -23.5505, lng = -46.6333) {
    if (mapa) return;
    
    mapa = L.map('mapa').setView([lat, lng], 15);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(mapa);
    
    // Marcador de localização do usuário
    if (userLocation) {
        L.circleMarker([userLocation.lat, userLocation.lng], {
            radius: 8,
            fillColor: '#6366f1',
            color: '#6366f1',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        })
        .bindPopup('📍 Sua localização')
        .addTo(mapa);
    }
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all nav tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active to nav tab
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    if (tabName === 'perfil') {
        carregarPerfil();
    }
    
    // Inicializar mapa quando mudar para aba buscar
    if (tabName === 'buscar' && !mapa) {
        setTimeout(() => {
            inicializarMapa(userLocation ? userLocation.lat : -23.5505, userLocation ? userLocation.lng : -46.6333);
        }, 100);
    }
    
    // Preencher select de tipos de ambiente na aba sensores
    if (tabName === 'sensores') {
        fetch(`${API_URL}/tipos-ambiente`)
            .then(r => r.json())
            .then(data => {
                const select = document.getElementById('sensoresTipoAmbiente');
                select.innerHTML = '<option value="">Selecione...</option>';
                data.tipos.forEach(tipo => {
                    const option = document.createElement('option');
                    option.value = tipo.valor;
                    option.textContent = tipo.valor;
                    select.appendChild(option);
                });
            })
            .catch(err => console.error('Erro ao carregar tipos:', err));
    }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('show');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('show');
    
    // Limpar campos
    if (modalId === 'loginModal') {
        document.getElementById('loginEmail').value = '';
        document.getElementById('loginSenha').value = '';
    } else if (modalId === 'registerModal') {
        document.getElementById('registerNome').value = '';
        document.getElementById('registerEmail').value = '';
        document.getElementById('registerSenha').value = '';
        document.getElementById('registerCidade').value = '';
    }
}

function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification show ${type}`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

function formatarData(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('pt-BR');
}

// ============= SENSORES =============

let medicaoRuido = null;
let medicaoLuminosidade = null;

async function medirRuidoSensor() {
    const btn = document.getElementById('btnMedirRuido');
    const status = document.getElementById('statusRuido');
    
    btn.disabled = true;
    status.className = 'sensores-status loading';
    status.textContent = '⏳ Capturando áudio... (3 segundos)';
    
    try {
        const dadosAudio = await sensorManager.medirRuido(3000);
        
        status.className = 'sensores-status sucesso';
        status.textContent = '✅ Áudio capturado! Processando...';
        
        // Processar no backend
        const resultado = await sensorManager.processarRuido(dadosAudio.frequencias, dadosAudio.energia_media);
        
        medicaoRuido = resultado;
        
        // Mostrar resultado
        document.getElementById('resultadoRuido').style.display = 'block';
        document.getElementById('resultadoRuidoValor').textContent = `${resultado.db_estimado} dB`;
        document.getElementById('resultadoRuidoNivel').innerHTML = 
            `<span class="nivel-badge nivel-${resultado.classificacao}">${resultado.classificacao}</span>`;
        
        // Atualizar resumo
        document.getElementById('resumoRuido').textContent = `${resultado.db_estimado} dB`;
        mostrarResumoSensores();
        
        status.className = 'sensores-status sucesso';
        status.textContent = `✅ Ruído medido: ${resultado.db_estimado} dB (${resultado.classificacao})`;
        
    } catch (error) {
        status.className = 'sensores-status erro';
        status.textContent = `❌ Erro: ${error.message}`;
        showNotification(error.message, 'error');
    } finally {
        btn.disabled = false;
        // Parar captura de áudio
        sensorManager.pararAudio();
    }
}

async function medirLuminosidadeSensor() {
    const btn = document.getElementById('btnMedirLuz');
    const status = document.getElementById('statusLuminosidade');
    
    btn.disabled = true;
    status.className = 'sensores-status loading';
    status.textContent = '⏳ Capturando vídeo... (2 segundos)';
    
    try {
        const dadosVideo = await sensorManager.medirLuminosidade(2000);
        
        status.className = 'sensores-status sucesso';
        status.textContent = '✅ Vídeo capturado! Processando...';
        
        // Processar no backend
        const resultado = await sensorManager.processarLuminosidade(dadosVideo.r, dadosVideo.g, dadosVideo.b);
        
        medicaoLuminosidade = resultado;
        
        // Mostrar resultado
        document.getElementById('resultadoLuminosidade').style.display = 'block';
        document.getElementById('resultadoLuminosidadeValor').textContent = `${resultado.lux_estimado} Lux`;
        document.getElementById('resultadoLuminosidadeNivel').innerHTML = 
            `<span class="nivel-badge nivel-${resultado.classificacao}">${resultado.classificacao}</span>`;
        
        // Atualizar resumo
        document.getElementById('resumoLuz').textContent = `${resultado.lux_estimado} Lux`;
        mostrarResumoSensores();
        
        status.className = 'sensores-status sucesso';
        status.textContent = `✅ Luz medida: ${resultado.lux_estimado} Lux (${resultado.classificacao})`;
        
    } catch (error) {
        status.className = 'sensores-status erro';
        status.textContent = `❌ Erro: ${error.message}`;
        showNotification(error.message, 'error');
    } finally {
        btn.disabled = false;
        // Parar captura de vídeo
        sensorManager.pararVideo();
    }
}

function mostrarResumoSensores() {
    if (medicaoRuido && medicaoLuminosidade) {
        document.getElementById('sensoresResumo').style.display = 'block';
    }
}

async function salvarMedicaoComSensores() {
    if (!authToken) {
        showNotification('Você precisa estar autenticado', 'error');
        return;
    }
    
    if (!medicaoRuido || !medicaoLuminosidade) {
        showNotification('Você precisa fazer ambas as medições', 'error');
        return;
    }
    
    const nomeLocal = document.getElementById('sensoresNomeLocal').value;
    const tipoAmbiente = document.getElementById('sensoresTipoAmbiente').value;
    
    if (!nomeLocal || !tipoAmbiente) {
        showNotification('Preencha nome e tipo de ambiente', 'error');
        return;
    }
    
    // Usar geolocalização do usuário ou padrão
    const latitude = userLocation ? userLocation.lat : -23.5505;
    const longitude = userLocation ? userLocation.lng : -46.6333;
    
    const body = {
        place_id: `${nomeLocal.replace(/\s+/g, '_')}_${Date.now()}`,
        nome_local: nomeLocal,
        endereco: "Medido via sensores do celular",
        tipo_ambiente: tipoAmbiente,
        coordenadas: {
            latitude: latitude,
            longitude: longitude
        },
        ruido_db: medicaoRuido.db_estimado,
        luminosidade_lux: medicaoLuminosidade.lux_estimado
    };
    
    try {
        const response = await fetch(`${API_URL}/registros`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(body)
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Erro ao criar registro');
        }
        
        showNotification('✅ Medição salva com sucesso!');
        
        // Limpar formulário
        document.getElementById('sensoresNomeLocal').value = '';
        document.getElementById('sensoresTipoAmbiente').value = '';
        document.getElementById('sensoresResumo').style.display = 'none';
        document.getElementById('resultadoRuido').style.display = 'none';
        document.getElementById('resultadoLuminosidade').style.display = 'none';
        document.getElementById('statusRuido').textContent = '';
        document.getElementById('statusLuminosidade').textContent = '';
        
        medicaoRuido = null;
        medicaoLuminosidade = null;
        
        carregarStats();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

