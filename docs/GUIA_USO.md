# 🧩 Ambientes Acessíveis - Guia de Uso

Um aplicativo que ajuda pessoas autistas e neurodivergentes a encontrar ambientes confortáveis e acessíveis, medindo ruído e luminosidade em locais públicos.

## 📋 Pré-requisitos

- Python 3.8+
- Pacotes instalados (veja `estrutura-back/requirements.txt`)

## 🚀 Como Executar

### 1️⃣ Iniciar o Backend (API)

```bash
cd estrutura-back
python3 main.py
```

A API estará disponível em: **http://localhost:8000**

Documentação interativa (Swagger): **http://localhost:8000/docs**

### 2️⃣ Iniciar o Frontend

Em outro terminal:

```bash
python3 serve_frontend.py
```

O Frontend estará disponível em: **http://localhost:3000**

## 🎯 Funcionalidades

### 👤 Autenticação
- **Registrar**: Crie uma conta com seu perfil (nome, email, cidade, neurodiversidade)
- **Login**: Acesse sua conta com email e senha
- **Perfil**: Visualize seus dados cadastrados

### 📍 Buscar Locais
- Procure por ambientes próximos
- Filtre por tipo (Restaurante, Biblioteca, Shopping, Hospital, Escola, Escritório, Parque, Cafeteria)
- Veja o nível atual de ruído e luminosidade
- Identifique locais com Selo Acessível (✅)

### 📊 Registrar Medições
- **Modo Manual**: Classifique o ambiente (Bom/Ok/Atenção/Ruim)
- **Modo Medido**: Insira valores em dB (ruído) e Lux (luminosidade)
- Locais com 100+ registros bom/ok ganham Selo Acessível

## 🎨 Estrutura do Frontend

```
frontend/
├── index.html       # Estrutura HTML
├── styles.css       # Estilos e responsividade
└── script.js        # Lógica e API
```

## 🔌 Endpoints da API

### Autenticação
- `POST /auth/registro` - Registrar novo usuário
- `POST /auth/login` - Fazer login
- `GET /auth/me` - Obter dados do usuário logado

### Locais
- `GET /locais/proximos` - Buscar locais próximos
- `GET /locais/{place_id}` - Obter detalhes de um local
- `POST /registros` - Criar novo registro de medição

### Informações
- `GET /tipos-ambiente` - Listar tipos de ambiente
- `GET /health` - Status da API
- `GET /` - Root

## 🎓 Normas Utilizadas

- **NBR 10152**: Níveis de ruído para conforto acústico
- **NBR 8995 / NBR 5413**: Iluminação para ambientes internos e externos

## 📱 Exemplo de Uso

1. **Registre-se**: Clique em "Registrar", preencha seus dados
2. **Explore locais**: Vá em "Buscar Locais" e procure ambientes
3. **Contribua**: Em "Registrar Leitura", meça e compartilhe dados
4. **Ganhe selos**: Após 100 registros bom/ok, o local ganha Selo Acessível

## 🛠️ Desenvolvimento

### Estrutura do Backend

```
estrutura-back/
├── main.py           # API FastAPI principal
├── db.py             # Configuração MongoDB
├── requirements.txt  # Dependências Python
└── docker-compose.yml # Docker setup (opcional)
```

### Tecnologias

- **Backend**: FastAPI, Uvicorn, JWT, Pydantic
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Banco de Dados**: MongoDB (configurável em db.py)
- **Autenticação**: JWT (JSON Web Tokens)

## 🐛 Troubleshooting

**Problema**: "CORS error" no frontend
- **Solução**: A API está configurada com CORS aberto. Reinicie ambos os servidores.

**Problema**: "Port already in use"
- **Solução**: Mude a porta em `main.py` ou `serve_frontend.py`

**Problema**: Não consegue acessar a API
- **Solução**: Verifique se a API está rodando em http://localhost:8000

## 📝 Notas

- Os dados estão em memória (simulados). Para produção, configure o MongoDB em `db.py`
- A autenticação usa JWT com token de 30 minutos de validade
- Coordenadas padrão são para São Paulo

## 📚 Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [NBR 10152](https://www.abntcatalogo.com.br)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Criado com ❤️ para tornar espaços mais acessíveis**
