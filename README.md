# 🌍 Sensorial MAP - App para Neurodivergentes

Um aplicativo web completo para medir, registrar e compartilhar a acessibilidade de ambientes públicos em relação a ruído e luminosidade. Desenvolvido especialmente para pessoas autistas e outras neurodiversidades que precisam encontrar espaços adequados ao seu perfil sensorial.

# Hackathon Atip
Esse aplicativo foi pensado das regras de negócio até a produção de prototipo para o Hackathon atip 2025, com o tema de acessibilidade.

## 📋 Tabela de Conteúdos

- [Visão Geral](#-visão-geral)
- [Características](#-características)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [API Endpoints](#-api-endpoints)
- [Estrutura de Pastas](#-estrutura-de-pastas)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Documentação Técnica](#-documentação-técnica)
- [Contribuindo](#-contribuindo)

## 🎯 Visão Geral

**Ambientes Acessíveis** é uma plataforma que permite aos usuários:
- Registrar medições de ruído e luminosidade em locais públicos
- Visualizar ambientes em um mapa interativo
- Consultar dados coletados pela comunidade
- Classificar ambientes de forma simples e intuitiva

O app utiliza sensores nativos do navegador (microfone e câmera) para capturar dados em tempo real, eliminando a necessidade de aplicativos externos.

### Para Quem?

- 👤 Pessoas autistas (TEA)
- 👤 Pessoas com TDAH
- 👤 Neurodivergentes em geral que precisam encontrar espaços seguros
- 👤 Administradores de espaços públicos que desejam adequar seus ambientes

## ✨ Características

### 🔐 Autenticação
- Registro e login com email
- Tokenização JWT segura
- Sessões persistentes com localStorage
- Perfil de usuário com informações de neurodiversidade

### 🗺️ Mapa Interativo
- Visualização em tempo real com OpenStreetMap
- Marcadores coloridos indicando nível de acessibilidade
  - 🟢 **Verde**: Bom (< 45 dB)
  - 🟡 **Laranja**: Ok (45-55 dB)
  - 🔴 **Vermelho**: Atenção/Ruim (> 55 dB)
- Zoom e navegação fluída
- Detalhes do local ao clicar em marcador

### 📊 Medições de Sensores
- **Ruído**: Captura via Web Audio API
  - Análise FFT em tempo real
  - Resultado em decibéis (dB)
  - Classificação automática
- **Luminosidade**: Captura via câmera
  - Análise de pixels em tempo real
  - Resultado em lux (Lux)
  - Correção gama automática

### 🔍 Busca e Filtro
- Busca por nome ou endereço do local
- Filtro por tipo de ambiente
- Resultados em tempo real

### 📝 Registro Manual
- Classificação rápida: Bom / Ok / Atenção / Ruim
- Salva automaticamente após medição por sensores
- Histórico de medições

### 🏅 Selo de Acessibilidade
- Local recebe "Selo Acessível" após 100 registros bom/ok no último mês
- Indica que o espaço é adequado para neurodivergentes

## 🏗️ Arquitetura do Projeto

```
sensorial_app/
├── estrutura-back/          # Backend API (FastAPI)
│   ├── main.py             # Servidor principal com todos os endpoints
│   ├── run_with_test_data.py # Script para iniciar com dados de teste
│   ├── requirements.txt      # Dependências Python
│   └── db.py               # Configuração de banco (MongoDB)
├── frontend_teste/          # Frontend (HTML5/CSS3/JS)
│   ├── index.html          # Interface principal
│   ├── script.js           # Lógica da aplicação
│   ├── sensores.js         # Classe SensorManager
│   ├── styles.css          # Estilos responsivos
│   └── serve_frontend.py   # Servidor local para frontend
└── docs/                    # Documentação técnica
    ├── ARQUITETURA.md      # Visão geral da arquitetura
    ├── MAPA_OPENSTREETMAP.md # Implementação do mapa
    ├── FLUXO_MEDICOES.md   # Fluxo de medições
    ├── SENSORES_TECNICO.md # Detalhes técnicos dos sensores
    └── TESTE_COM_DADOS_REAIS.md # Guia de testes
```

### Fluxo de Dados

```
┌─────────────────┐
│   Frontend      │ (HTML/CSS/JS)
│  - UI/UX        │
│  - Sensores     │
│  - Mapa         │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│   Backend       │ (FastAPI)
│  - API REST     │
│  - Validação    │
│  - Classificação│
│  - Persistência │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Database      │ (MongoDB*)
│  - Usuários     │
│  - Locais       │
│  - Registros    │
└─────────────────┘

* Atualmente em-memória (estrutura pronta para MongoDB)
```

## 📦 Pré-requisitos

- **Python 3.9+** (testado em 3.12.2)
- **Node.js** (opcional, apenas se quiser usar gerenciadores de pacotes)
- **Navegador moderno** (Chrome, Firefox, Safari, Edge)
- Permissões para:
  - ✅ Microfone (para medir ruído)
  - ✅ Câmera (para medir luminosidade)
  - ✅ Localização/GPS (para encontrar endereço)

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/codeonthespectrum/sensorial_app.git
cd sensorial_app
```

### 2. Crie um Ambiente Virtual Python

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instale as Dependências

```bash
pip install -r estrutura-back/requirements.txt
```

### 4. Execute o Backend

```bash
# Opção A: Com dados de teste pré-carregados
cd estrutura-back
python run_with_test_data.py

# Opção B: Backend limpo (sem dados)
cd estrutura-back
python main.py
```

O backend estará disponível em: `http://localhost:8000`

### 5. Execute o Frontend (em outro terminal)

```bash
cd frontend_teste
python serve_frontend.py
```

O frontend estará disponível em: `http://localhost:3000`

⚠️ **ATENÇÃO**
- O frontend descrito como `/front_test` são testes para visualização funcional do backend. A versão final ficará disponivel em 27/10/2025.

### 6. Acesse a Aplicação

Abra seu navegador e acesse: **http://localhost:3000**

## 💻 Como Usar

### Primeiro Acesso

1. **Registre uma conta**
   - Clique em "Não tem conta? Crie uma"
   - Preencha: Nome, Email, Senha, Cidade, Neurodiversidade
   - Clique em "Registrar"

2. **Escolha seu tipo de neurodiversidade**
   - TEA (Transtorno do Espectro Autista)
   - TDAH
   - Outro
   - Não informado

### Usando o Mapa

1. **Visualizar Locais**
   - Vá para a aba "Buscar"
   - O mapa carregará automaticamente
   - Vê marcadores coloridos dos ambientes registrados

2. **Filtrar Locais**
   - Digite um nome ou endereço na busca
   - Filtre por tipo de ambiente (Restaurante, Biblioteca, etc.)
   - O mapa se atualiza em tempo real

3. **Ver Detalhes**
   - Clique em um marcador no mapa
   - Verá: Nome, Endereço, Última medição, Total de registros

### Registrar Medições

#### Modo Automático (com Sensores)

1. Vá para aba "Sensores"
2. **Para Medir Ruído:**
   - Clique em "Medir Ruído"
   - Conceda permissão de microfone
   - Mantenha silêncio por 3 segundos
   - Resultado em dB aparecerá
3. **Para Medir Luminosidade:**
   - Clique em "Medir Luminosidade"
   - Conceda permissão de câmera
   - Aponte para o ambiente
   - Resultado em Lux aparecerá

#### Modo Manual (Classificação Rápida)

1. Vá para aba "Registrar"
2. Selecione um local
3. Escolha: **Bom** / **Ok** / **Atenção** / **Ruim**
4. Clique em "Registrar"

### Consultar Perfil

1. Vá para aba "Perfil"
2. Veja suas informações e histórico

## 🔌 API Endpoints

### Autenticação

```http
POST /auth/registro
Content-Type: application/json

{
  "nome": "João Silva",
  "email": "joao@example.com",
  "senha": "senha123",
  "cidade": "São Paulo",
  "neurodiversidade": "TEA"
}

Response: 201 Created
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

```http
POST /auth/login
Content-Type: application/json

{
  "email": "joao@example.com",
  "senha": "senha123"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

```http
GET /auth/me
Authorization: Bearer <token>

Response: 200 OK
{
  "nome": "João Silva",
  "email": "joao@example.com",
  "cidade": "São Paulo",
  "neurodiversidade": "TEA"
}
```

### Locais

```http
GET /locais/proximos?latitude=-23.5505&longitude=-46.6333&raio_km=5&tipo_ambiente=Restaurante

Response: 200 OK
{
  "locais": [
    {
      "place_id": "starbucks_paulista",
      "nome_local": "Starbucks Paulista",
      "tipo_ambiente": "Cafeteria",
      "coordenadas": {
        "latitude": -23.5612,
        "longitude": -46.6560
      },
      "nivel_ruido_atual": "Ok",
      "nivel_luz_atual": "Bom",
      "ultima_atualizacao": "2025-10-21T15:30:00",
      "selo_acessivel": false
    }
  ],
  "total": 1
}
```

```http
GET /locais/{place_id}

Response: 200 OK
{
  "place_id": "starbucks_paulista",
  "nome_local": "Starbucks Paulista",
  "tipo_ambiente": "Cafeteria",
  "coordenadas": {...},
  "nivel_ruido_atual": "Ok",
  "total_registros": 25,
  "selo_acessivel": false,
  "ultimos_5_registros": [...],
  "estatisticas_horario": [...]
}
```

### Registros

```http
POST /registros
Authorization: Bearer <token>
Content-Type: application/json

{
  "place_id": "starbucks_paulista",
  "nome_local": "Starbucks Paulista",
  "endereco": "Av. Paulista, 1000",
  "tipo_ambiente": "Cafeteria",
  "coordenadas": {
    "latitude": -23.5612,
    "longitude": -46.6560
  },
  "ruido_db": 48.5,
  "luminosidade_lux": 250
}

Response: 201 Created
{
  "mensagem": "Registro criado com sucesso",
  "id": 15,
  "nivel_ruido": "Ok",
  "nivel_luz": "Bom"
}
```

### Sensores

```http
POST /sensores/processar-audio
Content-Type: application/json

{
  "frequencias": [100, 200, 300, ...],
  "energia_media": 0.245
}

Response: 200 OK
{
  "db_estimado": 48.5,
  "energia_media": 0.245,
  "quantidade_frequencias": 128,
  "classificacao": "Ok"
}
```

```http
POST /sensores/processar-luminosidade
Content-Type: application/json

{
  "r": 200,
  "g": 210,
  "b": 190
}

Response: 200 OK
{
  "lux_estimado": 285.5,
  "luminancia": 0.478,
  "rgb": {"r": 200, "g": 210, "b": 190},
  "classificacao": "Bom"
}
```

```http
GET /health

Response: 200 OK
{
  "status": "ok",
  "timestamp": "2025-10-21T15:35:20",
  "usuarios_cadastrados": 15,
  "locais_cadastrados": 42,
  "registros_totais": 287
}
```

### Tipos de Ambiente

```http
GET /tipos-ambiente

Response: 200 OK
{
  "tipos": [
    {
      "valor": "Restaurante",
      "limites_ruido": {
        "bom": [0, 45],
        "ok": [45, 50],
        "atencao": [50, 55],
        "ruim": [55, 120]
      },
      "limites_luz": {...}
    },
    ...
  ]
}
```

### Informações de Sensores

```http
GET /sensores/info

Response: 200 OK
{
  "ruido": {
    "metodo": "Web Audio API",
    "descricao": "Captura áudio do microfone e analisa frequências",
    "precisao": "±3-5 dB",
    "limitacoes": [...]
  },
  "luminosidade": {...}
}
```

## 📂 Estrutura de Pastas

```
sensorial_app/
│
├── 📄 README.md                          # Este arquivo
├── 📄 .gitignore
├── 📄 LICENSE
│
├── 📁 estrutura-back/                    # Backend FastAPI
│   ├── 📄 main.py                        # API principal (588 linhas)
│   ├── 📄 run_with_test_data.py          # Startup com dados de teste
│   ├── 📄 requirements.txt                # Dependências Python
│   ├── 📄 db.py                          # Config MongoDB (template)
│   ├── 📄 api_test.sh                    # Scripts de teste
│   ├── 📄 test_api_interativo.py
│   ├── 📄 docker-compose.yml             # Config Docker (template)
│   └── 📁 __pycache__/
│
├── 📁 frontend_teste/                    # Frontend Web
│   ├── 📄 index.html                     # Template HTML (5 abas)
│   ├── 📄 script.js                      # Lógica principal (856 linhas)
│   ├── 📄 sensores.js                    # Classe SensorManager
│   ├── 📄 styles.css                     # Estilos responsivos
│   ├── 📄 serve_frontend.py              # Servidor local
│   └── 📄 sensores.js
│
├── 📁 docs/                              # Documentação Técnica
│   ├── 📄 ARQUITETURA.md                 # Visão geral do sistema
│   ├── 📄 MAPA_OPENSTREETMAP.md          # Docs do mapa
│   ├── 📄 FLUXO_MEDICOES.md              # Fluxo de medições
│   ├── 📄 SENSORES_TECNICO.md            # Detalhes técnicos
│   ├── 📄 GUIA_USO.md                    # Manual do usuário
│   └── 📄 TESTE_COM_DADOS_REAIS.md       # Guia de testes
│
└── 📁 .git/                              # Versionamento Git
```

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web assíncrono moderno
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validação de dados
- **PyJWT** - Tokenização JWT
- **Python 3.12** - Linguagem

### Frontend
- **HTML5** - Markup semântico
- **CSS3** - Estilos responsivos (Grid/Flexbox)
- **JavaScript Vanilla** - Zero dependências
- **Leaflet.js v1.9.4** - Mapa interativo
- **OpenStreetMap** - Tiles de mapa

### Sensores
- **Web Audio API** - Captura e análise de áudio
- **getUserMedia API** - Acesso à câmera
- **Canvas API** - Processamento de imagens

### Banco de Dados
- **Em-memória (Python dicts)** - Desenvolvimento
- **MongoDB** - Produção (estrutura pronta)

### DevOps
- **Docker** - Containerização (template incluso)
- **Git** - Versionamento

## 📚 Documentação Técnica

Acesse a documentação detalhada em `docs/`:

- **[ARQUITETURA.md](./docs/ARQUITETURA.md)** - Visão geral da arquitetura e fluxos
- **[MAPA_OPENSTREETMAP.md](./docs/MAPA_OPENSTREETMAP.md)** - Implementação do mapa com Leaflet.js
- **[FLUXO_MEDICOES.md](./docs/FLUXO_MEDICOES.md)** - Fluxo detalhado de medições
- **[SENSORES_TECNICO.md](./docs/SENSORES_TECNICO.md)** - Detalhes técnicos dos sensores
- **[TESTE_COM_DADOS_REAIS.md](./docs/TESTE_COM_DADOS_REAIS.md)** - Guia completo de testes
- **[GUIA_USO.md](./docs/GUIA_USO.md)** - Manual do usuário final

## 🧪 Testando a Aplicação

### Com Dados de Teste Pré-carregados

```bash
# Terminal 1: Backend com dados de teste
cd estrutura-back
python run_with_test_data.py

# Terminal 2: Frontend
cd frontend_teste
python serve_frontend.py

# Abrir browser
open http://localhost:3000
```

**Credenciais de Teste:**
- Email: `ana@test.com` | Senha: `senha123`
- Email: `carlos@test.com` | Senha: `senha123`
- Email: `maria@test.com` | Senha: `senha123`

### API Health Check

```bash
curl http://localhost:8000/health | python3 -m json.tool
```

### Documentação Interativa da API

```
http://localhost:8000/docs
```

## 🔐 Segurança

- ✅ JWT tokens para autenticação
- ✅ Hash SHA256 para senhas (em produção, use bcrypt)
- ✅ CORS habilitado para desenvolvimento
- ✅ Validação de entrada com Pydantic
- ✅ Limites de valor para sensores (dB: 0-120, Lux: 0-10000)

**Para Produção:**
- Configure `.env` com variáveis seguras
- Use bcrypt com passlib
- Configure CORS mais restritivo
- Implemente rate limiting
- Use HTTPS
- Configure MongoDB com autenticação

## 📊 Limites de Classificação (NBR/ABNT)

### Ruído (em decibéis - dB)

| Ambiente | Bom | Ok | Atenção | Ruim |
|----------|-----|----|---------:|------:|
| Restaurante | 0-45 | 45-50 | 50-55 | 55+ |
| Biblioteca | 0-35 | 35-40 | 40-45 | 45+ |
| Shopping | 0-50 | 50-55 | 55-60 | 60+ |
| Hospital | 0-35 | 35-40 | 40-45 | 45+ |
| Escritório | 0-45 | 45-50 | 50-55 | 55+ |

### Luminosidade (em lux - Lux)

| Ambiente | Bom | Ok | Atenção | Ruim |
|----------|-----|----|---------:|------:|
| Restaurante | 200-300 | 150-200 | 100-150 | 0-100 |
| Biblioteca | 300-500 | 250-300 | 200-250 | 0-200 |
| Escritório | 500-750 | 400-500 | 300-400 | 0-300 |

## 🚧 Roadmap

### v1.0 ✅
- ✅ Autenticação e perfil de usuário
- ✅ Mapa interativo com marcadores
- ✅ Web Audio API para ruído
- ✅ Camera API para luminosidade
- ✅ Busca e filtro de locais
- ✅ Registro manual

### v1.1 🔄
- 🔄 Persistência em MongoDB
- 🔄 Calibração de sensores por usuário
- 🔄 Histórico gráfico de medições
- 🔄 Estatísticas por horário

### v2.0 📋
- 📋 App mobile (React Native/Flutter)
- 📋 Notificações em tempo real
- 📋 Comunidades por bairro
- 📋 Relatórios para administradores
- 📋 Integração com Google Places API

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

### Diretrizes
- Código deve estar bem documentado
- Testes devem passar
- Siga a style guide do projeto
- Atualize a documentação conforme necessário

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **Gabrielly Gomes** - Dev Backend
- **Katiene Souza** - Dev Frontend
- **Stefanni Nascimento** - UI Designer
- **Jefferson Lima** - UX Designer
- **Beatriz Ferreira** - Business
- **Giovana** - Business


## 📞 Suporte

- 🐛 Encontrou um bug? [Abra uma issue](https://github.com/codeonthespectrum/sensorial_app/issues)
- 💡 Tem uma sugestão? Comente em [Discussions](https://github.com/codeonthespectrum/sensorial_app/discussions)
- 📧 Email: [suporte@codeospectrum.com](mailto:suporte@codeospectrum.com)

## 🙏 Agradecimentos

- OpenStreetMap pelos mapas
- FastAPI pela excelente documentação
- Comunidade autista por inspirar este projeto
- Todos os contribuidores e testadores

---

**Desenvolvido com ❤️ para tornar o mundo mais acessível para neurodivergentes.**

**Última atualização:** 21 de outubro de 2025
