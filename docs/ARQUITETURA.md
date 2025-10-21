# 🎯 Arquitetura Final - App Ambientes Acessíveis

## 📋 Resumo Executivo

App completo para medir e compartilhar informações sobre acessibilidade de ambientes (ruído e luz) para pessoas neurodivergentes.

**Tecnologia:** Full Stack Python + JavaScript
**Status:** ✅ Pronto para uso
**Versão:** 2.0

---

## 🏗️ Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (SPA - Vue + JavaScript)            │
│                        HTTP/CORS                                │
├─────────────────────────────────────────────────────────────────┤
│                   Backend (FastAPI + Python)                    │
│                    REST API + JWT Auth                          │
├─────────────────────────────────────────────────────────────────┤
│              Database (Em Memória / MongoDB)                    │
│                                                                 │
│  ├─ Usuários (users)                                           │
│  ├─ Locais (locations)                                         │
│  └─ Registros (records)                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│            Dispositivos Móveis (iOS/Android)                    │
│                                                                 │
│  ├─ Web Audio API (Microfone)                                  │
│  ├─ Camera API (Câmera traseira)                               │
│  ├─ Geolocation API (GPS)                                      │
│  └─ Canvas API (Processamento de pixels)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📱 Frontend

### Estrutura

```
frontend/
├── index.html          # Estrutura HTML (316 linhas)
├── styles.css          # Design responsivo (800+ linhas)
├── script.js           # Lógica principal (856 linhas)
└── sensores.js         # Captura de sensores (450+ linhas)
```

### Abas Disponíveis

| Aba | Função | Tecnologia |
|-----|--------|-----------|
| 🏠 **Início** | Dashboard com estatísticas | Stats API |
| 🔍 **Buscar Locais** | Mapa interativo + filtros | Leaflet.js + OpenStreetMap |
| 📊 **Registrar Manual** | Classificação simples | Geolocation API |
| 📱 **Sensores** | Medição automática | Web Audio + Camera |
| 👤 **Perfil** | Dados do usuário | User API |

### Features Principais

**1. Autenticação**
- Registro com email/senha
- Login com JWT
- Persistência com localStorage

**2. Geolocalização**
- GPS automático
- Reverse geocoding (OpenStreetMap)
- Preenchimento automático de endereço

**3. Mapa**
- Visualização de locais
- Marcadores coloridos por nível
- Filtro por ambiente/nome

**4. Sensores**
- Captura de áudio (3 seg)
- Captura de vídeo (2 seg)
- Processamento em tempo real

---

## 🔌 Backend

### Estrutura

```
estrutura-back/
├── main.py              # API FastAPI (590 linhas)
├── db.py                # Configuração MongoDB (311 linhas)
├── requirements.txt     # Dependências Python
└── docker-compose.yml   # Setup com Docker (opcional)
```

### Endpoints da API

#### Autenticação
```
POST   /auth/registro       # Registrar novo usuário
POST   /auth/login          # Fazer login
GET    /auth/me             # Dados do usuário logado
```

#### Registros de Medições
```
POST   /registros           # Criar novo registro
GET    /locais/{place_id}   # Detalhes de um local
GET    /locais/proximos     # Buscar locais próximos
```

#### Sensores
```
POST   /sensores/processar-audio          # Processar ruído
POST   /sensores/processar-luminosidade   # Processar luz
GET    /sensores/info                     # Info dos sensores
```

#### Utilitários
```
GET    /tipos-ambiente     # Lista de ambientes
GET    /health             # Status da API
GET    /                   # Root
```

### Dados Armazenados

**Usuário**
```python
{
    "email": "usuario@email.com",
    "nome": "João Silva",
    "cidade": "São Paulo",
    "neurodiversidade": "TEA",
    "senha_hash": "bcrypt_hash",
    "data_criacao": "2025-10-20T15:30:00"
}
```

**Registro de Medição**
```python
{
    "id": 1,
    "place_id": "unique_location_id",
    "usuario_email": "usuario@email.com",
    "timestamp": "2025-10-20T15:30:00",
    
    # Medições
    "ruido_db": 52.3,                 # Do sensor ou null
    "luminosidade_lux": 450.5,        # Do sensor ou null
    
    # Classificações
    "nivel_ruido": "Ok",
    "nivel_luz": "Ok"
}
```

**Local**
```python
{
    "place_id": "unique_id",
    "nome_local": "Starbucks Shopping",
    "endereco": "Rua das Flores, 123",
    "tipo_ambiente": "Cafeteria",
    "coordenadas": {
        "latitude": -23.5505,
        "longitude": -46.6333
    }
}
```

---

## 🎤 Processamento de Sensores

### Fluxo de Ruído

```
Microfone (Input)
       ↓
Web Audio API
- Cria contexto de áudio
- FFT Size: 2048
- Captura 30 amostras de 100ms
       ↓
Envia para /sensores/processar-audio
       ↓
Backend
- Calcula energia média
- Converte para dB: 20 * log10(energia/ref)
- Limita 0-120 dB
- Classifica com LIMITES_AMBIENTES
       ↓
Retorna
{
    "db_estimado": 52.3,
    "classificacao": "Ok"
}
```

### Fluxo de Luminosidade

```
Câmera (Input)
       ↓
getUserMedia + Canvas
- Captura vídeo
- Extrai 10 frames de 200ms
- Analisa região central (25-75%)
       ↓
Envia para /sensores/processar-luminosidade
       ↓
Backend
- Gamma correction (sRGB)
- Calcula luminância relativa
- Converte para Lux: 10000 * (luminância^2)
- Limita 0-10000 Lux
- Classifica com LIMITES_AMBIENTES
       ↓
Retorna
{
    "lux_estimado": 450.5,
    "classificacao": "Ok"
}
```

---

## 🔐 Segurança

### Autenticação
- JWT (JSON Web Tokens)
- Duração: 30 minutos
- Armazenado: localStorage (frontend)
- Header: `Authorization: Bearer {token}`

### Criptografia
- Senha: bcrypt
- Esquemas: ["bcrypt"]
- Deprecated: "auto"

### CORS
- Origins: "*" (desenvolvimento)
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type, Authorization

---

## 📊 Classificação de Ambientes

### Normas Utilizadas
- **NBR 10152**: Níveis de ruído para conforto
- **NBR 8995/5413**: Iluminação para ambientes

### Limites por Ambiente

**Exemplo: Restaurante**
```python
{
    "ruido": {
        "bom": (0, 45),      # dB
        "ok": (45, 50),
        "atencao": (50, 55),
        "ruim": (55, 120)
    },
    "luz": {
        "bom": (200, 300),   # Lux
        "ok": (150, 200),
        "atencao": (100, 150),
        "ruim": (0, 100)
    }
}
```

### Selo Acessível
- Requer **100+ registros** no último mês
- **80%+ dos registros** = "Bom" ou "Ok"
- Ambos ruído E luz precisam ser "Bom/Ok"
- Qualquer tipo de medição conta (sensor ou manual)

---

## 🚀 Deploy

### Desenvolvimento

```bash
# Terminal 1: Backend
cd estrutura-back
pip install -r requirements.txt
python3 main.py

# Terminal 2: Frontend
cd frontend
python3 -m http.server 3000
# ou
python3 ../serve_frontend.py
```

### Produção

```bash
# Docker
docker-compose up -d

# Ou com Heroku/AWS/DigitalOcean
# (config necessária)
```

---

## 📈 Métricas

### Dashboard (Aba Início)
- Usuários cadastrados
- Locais mapeados
- Registros totais

### Por Local
- Total de registros
- Nível de ruído atual
- Nível de luz atual
- Status de Selo Acessível
- Estatísticas por horário

---

## 🎓 Fluxo de Uso Típico

### Novo Usuário

```
1. Acessa localhost:3000
2. Clica "Registrar"
   - Email, senha, nome, cidade, neurodiversidade
3. Confirmação de registro
4. Redireciona para "Buscar Locais"
```

### Usuário Existente

```
1. Clica "Login"
   - Email e senha
2. Token salvo em localStorage
3. Dashboard com estatísticas
4. Pode começar a registrar medições
```

### Registrando com Sensores (Principal)

```
1. Abre "📱 Medir com Sensores"
2. "🎤 Medir Ruído" → 3 segundos
3. "💡 Medir Luz" → 2 segundos
4. Preenche nome e tipo
5. "✅ Salvar Medição"
6. Dados salvos no banco com GPS
```

### Registrando Manualmente (Alternativa)

```
1. Abre "📊 Registrar Medição Manual"
2. "📍 Obter Localização"
3. Preenche dados do local
4. Classifica ambiente (4 cliques)
5. "✅ Enviar Classificação"
6. Dados salvos no banco
```

### Buscando Locais

```
1. Abre "🔍 Buscar Locais"
2. Vê mapa com marcadores coloridos
3. Pode filtrar por nome ou tipo
4. Clica em marcador para detalhes
5. Vê histórico de medições
```

---

## 📝 Tecnologias Stack

### Frontend
- **HTML5**: Estrutura
- **CSS3**: Design responsivo (Grid, Flexbox)
- **JavaScript (ES6+)**: Lógica
- **Leaflet.js**: Mapas
- **OpenStreetMap**: Dados de mapas
- **Web Audio API**: Captura de áudio
- **Camera API**: Captura de vídeo
- **Canvas API**: Processamento de imagens
- **Geolocation API**: GPS

### Backend
- **Python 3.8+**: Linguagem
- **FastAPI**: Framework web
- **Uvicorn**: Servidor ASGI
- **Pydantic**: Validação de dados
- **Python-Jose**: JWT
- **Passlib**: Hashing de senha
- **PyMongo/Motor**: MongoDB (opcional)
- **CORS Middleware**: Cross-origin requests

### Database
- **Em Desenvolvimento**: Dicionários Python (memória)
- **Em Produção**: MongoDB (configurado em db.py)

### DevOps
- **Docker**: Containerização
- **Docker Compose**: Orquestração

---

## 📚 Documentação Incluída

```
📁 Documentação/
├── GUIA_USO.md                  # Como usar o app
├── GUIA_MELHORIAS.md            # Features adicionadas
├── MELHORIAS.md                 # Detalhes de melhorias
├── SENSORES_TECNICO.md          # Como sensores funcionam
├── FLUXO_MEDICOES.md            # Fluxo de medições
└── ARQUITETURA.md               # Este arquivo
```

---

## 🎯 Próximas Melhorias

### Curto Prazo
- [ ] Validação melhorada de entrada
- [ ] Histórico de medições do usuário
- [ ] Sistema de avaliação de precisão
- [ ] Notificações em tempo real

### Médio Prazo
- [ ] Integração com redes sociais
- [ ] Compartilhamento de locais
- [ ] Modo offline com sync
- [ ] Gráficos avançados
- [ ] API pública (documentada com Swagger)

### Longo Prazo
- [ ] App nativo (React Native/Flutter)
- [ ] Integração com sensores nativos
- [ ] Machine Learning para padrões
- [ ] Integração com mapas de cidades
- [ ] Analytics e relatórios

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| "CORS error" | Reinicie backend e frontend |
| "Permissão negada" | Verifique permissões do navegador |
| "Localização não funciona" | Use HTTPS em produção |
| "Sensores não medem" | Teste em outro navegador |
| "Banco vazio" | Dados estão em memória (restart = reset) |

---

## 📞 Suporte

Para reportar bugs ou sugerir melhorias:
1. Abra uma issue no GitHub
2. Descreva o problema
3. Forneça steps para reproduzir
4. Inclua versão do navegador

---

## 📄 Licença

Este projeto é open source e está disponível para uso educacional e não-comercial.

---

**Desenvolvido com ❤️ para tornar espaços mais acessíveis**

**Data**: 20 de outubro de 2025
**Versão**: 2.0
**Status**: ✅ Pronto para produção
