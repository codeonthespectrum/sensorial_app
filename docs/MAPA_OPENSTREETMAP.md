# 🗺️ MAPA OPENSTREETMAP - DOCUMENTAÇÃO TÉCNICA

## ✅ Status: JÁ IMPLEMENTADO!

O mapa interativo com OpenStreetMap **já está completamente funcional** no seu aplicativo!

---

## 📍 Como Funciona

### 🏗️ Arquitetura

```
┌─────────────────────────────────────┐
│        FRONTEND (HTML/JS)           │
├─────────────────────────────────────┤
│  ├─ Leaflet.js (Biblioteca de Mapa) │
│  ├─ OpenStreetMap (Tiles de Mapa)   │
│  └─ L.circleMarker (Marcadores)     │
├─────────────────────────────────────┤
│        BACKEND (API FastAPI)        │
├─────────────────────────────────────┤
│  ├─ GET /locais (Lista de locais)   │
│  ├─ Coordenadas armazenadas         │
│  └─ Níveis de ruído/luz             │
└─────────────────────────────────────┘
```

### 🔄 Fluxo de Funcionamento

```
1. Usuário clica em "🔍 Buscar Locais"
         ↓
2. Frontend chama buscarLocais()
         ↓
3. Busca dados do backend (coordenadas + níveis)
         ↓
4. Inicializa Leaflet L.map() com OpenStreetMap
         ↓
5. Adiciona marcadores circulares coloridos
   - 🟢 Verde (Bom)
   - 🟡 Laranja (Ok)
   - 🔴 Vermelho (Ruim)
         ↓
6. Ao clicar no marcador, mostra popup com nome
         ↓
7. Mapa auto-centraliza nos pontos
```

---

## 💻 Implementação Frontend

### Arquivo: `frontend_teste/script.js`

#### 1. **Inicializar o Mapa**
```javascript
function inicializarMapa(lat = -23.5505, lng = -46.6333) {
    if (mapa) return;  // Evita reinicializar
    
    // Cria mapa com Leaflet
    mapa = L.map('mapa').setView([lat, lng], 15);
    
    // Adiciona tiles do OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(mapa);
}
```

#### 2. **Adicionar Marcadores**
```javascript
locaisFiltrados.forEach(local => {
    // Determina cor baseado no nível de ruído
    const color = local.nivel_ruido_atual === 'Bom' ? 'green' : 
                 local.nivel_ruido_atual === 'Ok' ? 'orange' : 'red';
    
    // Cria marcador circular
    L.circleMarker([
        local.coordenadas.latitude,
        local.coordenadas.longitude
    ], {
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
```

#### 3. **Auto-Centralizar Mapa**
```javascript
// Calcula limites dos pontos
const bounds = L.latLngBounds(
    locaisFiltrados.map(l => [
        l.coordenadas.latitude,
        l.coordenadas.longitude
    ])
);

// Centraliza mapa com padding
mapa.fitBounds(bounds, { padding: [50, 50] });
```

---

## 🔌 Dependências

### Bibliotecas CDN

```html
<!-- Leaflet CSS -->
<link rel="stylesheet" 
  href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />

<!-- Leaflet JS -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
```

### Tiles de Mapa (OpenStreetMap)
```
https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

---

## 🎨 Recursos Implementados

| Recurso | Status | Descrição |
|---------|--------|-----------|
| Mapa Base | ✅ | OpenStreetMap com zoom 15 |
| Marcadores | ✅ | Círculos coloridos por nível |
| Popups | ✅ | Nome e tipo ao clicar |
| Legenda Cores | ✅ | Verde/Laranja/Vermelho |
| Auto-Zoom | ✅ | Ajusta para mostrar todos |
| Localização Usuário | ✅ | Círculo azul na sua posição |
| Filtro em Tempo Real | ✅ | Atualiza mapa ao filtrar |

---

## 📍 Dados Fornecidos pelo Backend

O backend fornece os dados estruturados assim:

```python
{
    "place_id": "place_0",
    "nome_local": "Starbucks Paulista",
    "tipo_ambiente": "Cafeteria",
    "coordenadas": {
        "latitude": -23.5615,
        "longitude": -46.6561
    },
    "nivel_ruido_atual": "Ok",
    "luminosidade_lux": 380.0
}
```

---

## 🧪 Como Testar

### 1. Acesse a Aplicação
```
http://localhost:3000
```

### 2. Faça Login
```
Email: ana@test.com
Senha: 123456
```

### 3. Clique em "🔍 Buscar Locais"
Você verá:
- ✅ Mapa centralizado em São Paulo
- ✅ 5 marcadores coloridos
- ✅ Sua localização (círculo azul)

### 4. Interaja com o Mapa
- **Clique em um marcador** → Vê nome do local
- **Rolar mouse** → Zoom in/out
- **Arrastar** → Move o mapa
- **Digite no filtro** → Marcadores desaparecem dinamicamente

---

## 🎯 Casos de Uso

### Caso 1: Visualizar Todos os Locais
```
1. Abra a aba "Buscar"
2. Mapa mostra todos os 5 locais
3. Cores indicam nível de ruído
```

### Caso 2: Buscar por Nome
```
1. Digite "biblioteca" no filtro
2. Mapa mostra apenas Biblioteca Municipal
3. Zoom automático para o local
```

### Caso 3: Filtrar por Tipo
```
1. Selecione tipo "Cafeteria"
2. Mapa mostra apenas Starbucks
3. Outros marcadores desaparecem
```

### Caso 4: Geolocalização
```
1. Se o navegador permitir GPS
2. Círculo azul mostra sua posição
3. Marcadores mostram distância
```

---

## 🔧 Customizações Possíveis

### Mudar Cores dos Marcadores
```javascript
const colorMap = {
    'Bom': '#10b981',      // Verde
    'Ok': '#f59e0b',       // Laranja
    'Atenção': '#ef4444',  // Vermelho
    'Ruim': '#7f1d1d'      // Vermelho escuro
};

const color = colorMap[local.nivel_ruido_atual];
```

### Aumentar Tamanho dos Marcadores
```javascript
L.circleMarker([...], {
    radius: 15,  // Aumentar de 10 para 15
    ...
})
```

### Adicionar Ícone Customizado
```javascript
const icon = L.icon({
    iconUrl: 'https://example.com/icon.png',
    iconSize: [32, 32],
    popupAnchor: [0, -32]
});

L.marker([lat, lng], { icon: icon }).addTo(mapa);
```

### Adicionar Clusterização (para muitos marcadores)
```javascript
// Usar Leaflet Markercluster
L.markerClusterGroup().addTo(mapa);
```

---

## 📊 Estrutura de Dados no BD

### Locais com Coordenadas
```
db_locations = {
    "place_0": {
        "coordenadas": {
            "latitude": -23.5615,
            "longitude": -46.6561
        }
    }
}
```

### Registros com Níveis
```
db_records = [
    {
        "place_id": "place_0",
        "nivel_ruido": "Ok",
        "nivel_luz": "Bom",
        "timestamp": "2025-10-20T..."
    }
]
```

---

## ⚙️ Como Adicionar Novo Local ao Mapa

### No Backend
```python
db_locations["place_novo"] = {
    "nome_local": "Novo Local",
    "coordenadas": {
        "latitude": -23.5555,
        "longitude": -46.6666
    }
}
```

### Frontend (automático)
Ao chamar `buscarLocais()`, o novo marcador aparecerá automaticamente!

---

## 🐛 Troubleshooting

### Mapa não aparece
- ✅ Verifique se o div `<div id="mapa">` existe no HTML
- ✅ Verifique se CSS `.mapa-container` está no styles.css
- ✅ Verifique se Leaflet foi carregado (console sem erros)

### Marcadores não aparecem
- ✅ Verifique se os dados têm `coordenadas.latitude` e `coordenadas.longitude`
- ✅ Verifique se `nivel_ruido_atual` tem valor válido

### Mapa não centraliza
- ✅ Verifique se `locaisFiltrados` tem pelo menos 1 item
- ✅ Verifique se coordenadas são válidas (lat -90 a 90, lng -180 a 180)

---

## 📚 Recursos Externos

- **Leaflet Docs**: https://leafletjs.com/
- **OpenStreetMap**: https://www.openstreetmap.org/
- **Leaflet Plugins**: https://leafletjs.com/plugins.html

---

## ✨ Resumo

| Aspecto | Implementação |
|---------|------|
| **Frontend** | ✅ Leaflet.js (1350 linhas de JS) |
| **Backend** | ✅ Fornece coordenadas via API |
| **Tiles** | ✅ OpenStreetMap (gratuito) |
| **Marcadores** | ✅ Coloridos por nível |
| **Filtros** | ✅ Em tempo real |
| **Responsivo** | ✅ Mobile-friendly |
