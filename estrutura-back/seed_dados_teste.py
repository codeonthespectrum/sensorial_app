"""
Script para popular o banco de dados com dados de teste realistas.
Cria usuários, locais e registros de medições.
"""

import requests
import json
from datetime import datetime, timedelta
from random import choice, randint, uniform
import time

BASE_URL = "http://localhost:8000"

# Cores para terminal
VERDE = '\033[92m'
AZUL = '\033[94m'
AMARELO = '\033[93m'
VERMELHO = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_sucesso(msg):
    print(f"{VERDE}✅ {msg}{RESET}")

def print_info(msg):
    print(f"{AZUL}ℹ️  {msg}{RESET}")

def print_alerta(msg):
    print(f"{AMARELO}⚠️  {msg}{RESET}")

def print_erro(msg):
    print(f"{VERMELHO}❌ {msg}{RESET}")

def print_titulo(msg):
    print(f"\n{BOLD}{AZUL}{'='*60}{RESET}")
    print(f"{BOLD}{AZUL}{msg}{RESET}")
    print(f"{BOLD}{AZUL}{'='*60}{RESET}\n")

# ============================================================================
# DADOS DE TESTE
# ============================================================================

USUARIOS = [
    {
        "email": "ana.silva@email.com",
        "senha": "senha123",
        "nome": "Ana Silva",
        "cidade": "São Paulo",
        "neurodiversidade": "TEA"
    },
    {
        "email": "carlos.santos@email.com",
        "senha": "senha123",
        "nome": "Carlos Santos",
        "cidade": "São Paulo",
        "neurodiversidade": "TDAH"
    },
    {
        "email": "maria.oliveira@email.com",
        "senha": "senha123",
        "nome": "Maria Oliveira",
        "cidade": "São Paulo",
        "neurodiversidade": "Sensibilidade Sensorial"
    }
]

LOCAIS = [
    {
        "nome_local": "Starbucks Paulista",
        "endereco": "Avenida Paulista, 1000 - São Paulo",
        "tipo_ambiente": "Cafeteria",
        "coordenadas": {"latitude": -23.5615, "longitude": -46.6561}
    },
    {
        "nome_local": "Biblioteca Municipal",
        "endereco": "Rua dos Gusmões, 123 - Centro - São Paulo",
        "tipo_ambiente": "Biblioteca",
        "coordenadas": {"latitude": -23.5512, "longitude": -46.6345}
    },
    {
        "nome_local": "Shopping Imigrantes",
        "endereco": "Avenida Imigrantes, 1555 - São Bernardo do Campo",
        "tipo_ambiente": "Shopping",
        "coordenadas": {"latitude": -23.6489, "longitude": -46.5779}
    },
    {
        "nome_local": "Restaurante Italiano Bella Italia",
        "endereco": "Rua da Consolação, 500 - São Paulo",
        "tipo_ambiente": "Restaurante",
        "coordenadas": {"latitude": -23.5545, "longitude": -46.6559}
    },
    {
        "nome_local": "Metrô Republica",
        "endereco": "Praça da República - São Paulo",
        "tipo_ambiente": "Transporte Público",
        "coordenadas": {"latitude": -23.5497, "longitude": -46.6349}
    },
    {
        "nome_local": "SESC Pompeia",
        "endereco": "Rua Clélia, 93 - São Paulo",
        "tipo_ambiente": "Centro Cultural",
        "coordenadas": {"latitude": -23.5310, "longitude": -46.6700}
    },
    {
        "nome_local": "Livraria Cultura",
        "endereco": "Avenida Paulista, 901 - São Paulo",
        "tipo_ambiente": "Livraria",
        "coordenadas": {"latitude": -23.5605, "longitude": -46.6548}
    }
]

# Níveis reais de ruído (em dB)
NIVEIS_RUIDO = [35, 42, 48, 52, 55, 62, 68, 72, 78]

# Níveis reais de luminosidade (em Lux)
NIVEIS_LUX = [150, 250, 400, 500, 800, 1200, 1800, 3000, 5000]

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def registrar_usuario(usuario):
    """Registra um novo usuário"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/registro",
            json=usuario,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            print_sucesso(f"Usuário registrado: {usuario['nome']}")
            return data.get("email")
        elif response.status_code == 400:
            print_alerta(f"Usuário {usuario['email']} já existe")
            return usuario["email"]
        else:
            print_erro(f"Erro ao registrar {usuario['nome']}: {response.status_code}")
            return None
    except Exception as e:
        print_erro(f"Exceção ao registrar {usuario['nome']}: {str(e)}")
        return None

def fazer_login(email, senha):
    """Faz login e retorna o token JWT"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "senha": senha},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print_erro(f"Erro ao fazer login: {response.status_code}")
            return None
    except Exception as e:
        print_erro(f"Exceção ao fazer login: {str(e)}")
        return None

def criar_registro(token, lugar_index, tipo_medida="sensor"):
    """Cria um registro de medição"""
    try:
        local = LOCAIS[lugar_index]
        
        # Gera dados realistas baseados no tipo de ambiente
        if tipo_medida == "sensor":
            # Sensor: valores precisos
            if local["tipo_ambiente"] == "Biblioteca":
                ruido_db = uniform(30, 45)
                luminosidade_lux = uniform(200, 400)
            elif local["tipo_ambiente"] == "Cafeteria":
                ruido_db = uniform(55, 70)
                luminosidade_lux = uniform(300, 500)
            elif local["tipo_ambiente"] == "Shopping":
                ruido_db = uniform(65, 80)
                luminosidade_lux = uniform(500, 1000)
            elif local["tipo_ambiente"] == "Restaurante":
                ruido_db = uniform(60, 75)
                luminosidade_lux = uniform(200, 400)
            elif local["tipo_ambiente"] == "Transporte Público":
                ruido_db = uniform(70, 85)
                luminosidade_lux = uniform(100, 300)
            elif local["tipo_ambiente"] == "Centro Cultural":
                ruido_db = uniform(40, 55)
                luminosidade_lux = uniform(400, 700)
            elif local["tipo_ambiente"] == "Livraria":
                ruido_db = uniform(35, 50)
                luminosidade_lux = uniform(300, 500)
            else:
                ruido_db = uniform(50, 65)
                luminosidade_lux = uniform(300, 600)
            
            registro = {
                "place_id": f"place_{lugar_index}",
                "nome_local": local["nome_local"],
                "tipo_ambiente": local["tipo_ambiente"],
                "coordenadas": local["coordenadas"],
                "ruido_db": round(ruido_db, 1),
                "luminosidade_lux": round(luminosidade_lux, 1)
            }
        else:
            # Classificação manual
            classificacoes = ["Bom", "Ok", "Atenção", "Ruim"]
            registro = {
                "place_id": f"place_{lugar_index}",
                "nome_local": local["nome_local"],
                "tipo_ambiente": local["tipo_ambiente"],
                "coordenadas": local["coordenadas"],
                "nivel_ruido_manual": choice(classificacoes),
                "nivel_luz_manual": choice(classificacoes)
            }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/registros",
            json=registro,
            headers=headers,
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            print_sucesso(f"Registro criado: {local['nome_local']} ({tipo_medida})")
            return True
        else:
            print_erro(f"Erro ao criar registro: {response.status_code}")
            if response.text:
                print_alerta(f"Response: {response.text[:100]}")
            return False
    except Exception as e:
        print_erro(f"Exceção ao criar registro: {str(e)}")
        return False

def obter_status():
    """Obtém status atual do banco"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# ============================================================================
# MAIN
# ============================================================================

def main():
    print_titulo("🌱 POPULANDO BANCO DE DADOS COM DADOS DE TESTE")
    
    # Verifica se a API está rodando
    print_info("Verificando se a API está rodando...")
    if not obter_status():
        print_erro("API não está respondendo em http://localhost:8000")
        print_alerta("Inicie o backend com: cd estrutura-back && python3 main.py")
        return
    
    print_sucesso("API respondendo corretamente!")
    
    # ========================================================================
    # 1. REGISTRAR USUÁRIOS
    # ========================================================================
    print_titulo("📝 ETAPA 1: REGISTRANDO USUÁRIOS")
    
    emails_registrados = []
    for usuario in USUARIOS:
        email = registrar_usuario(usuario)
        if email:
            emails_registrados.append(email)
        time.sleep(0.5)
    
    print_info(f"Total de usuários registrados: {len(emails_registrados)}")
    
    # ========================================================================
    # 2. FAZER LOGIN E CRIAR REGISTROS
    # ========================================================================
    print_titulo("🔒 ETAPA 2: FAZENDO LOGIN E CRIANDO REGISTROS")
    
    for email in emails_registrados:
        senha = "senha123"
        print_info(f"Fazendo login com {email}...")
        
        token = fazer_login(email, senha)
        if not token:
            continue
        
        print_sucesso(f"Login realizado! Token recebido")
        
        # Cria 3-5 registros por usuário
        num_registros = randint(3, 5)
        locais_indices = list(range(len(LOCAIS)))
        choice(locais_indices)  # Embaralha
        
        for i in range(min(num_registros, len(LOCAIS))):
            lugar_idx = i
            tipo_medida = choice(["sensor", "sensor", "sensor", "manual"])
            
            criar_registro(token, lugar_idx, tipo_medida)
            time.sleep(0.3)
    
    # ========================================================================
    # 3. STATUS FINAL
    # ========================================================================
    print_titulo("📊 STATUS FINAL DO BANCO DE DADOS")
    
    time.sleep(1)
    status = obter_status()
    
    if status:
        print(f"""
{VERDE}✅ DADOS DE TESTE CRIADOS COM SUCESSO!{RESET}

{BOLD}Resumo:{RESET}
  👥 Usuários cadastrados: {status['usuarios_cadastrados']}
  📍 Locais cadastrados: {status['locais_cadastrados']}
  📊 Registros totais: {status['registros_totais']}

{BOLD}Próximas ações:{RESET}
  1. Acesse http://localhost:3000
  2. Faça login com:
     Email: {emails_registrados[0] if emails_registrados else 'ana.silva@email.com'}
     Senha: senha123
  3. Explore os dados no mapa e tabelas
  4. Teste adicionar novos registros
        """)
    else:
        print_erro("Não foi possível obter status final")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{AMARELO}⏸️  Operação cancelada pelo usuário{RESET}")
    except Exception as e:
        print_erro(f"Erro fatal: {str(e)}")
