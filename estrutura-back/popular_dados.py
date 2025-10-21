#!/usr/bin/env python3
"""
Script simples para testar e popular o banco de dados com dados de teste.
Sem dependências externas além de requests.
"""

import requests
import json
import time
from random import choice, randint, uniform

BASE_URL = "http://localhost:8000"

# Cores
VERDE = '\033[92m'
AZUL = '\033[94m'
AMARELO = '\033[93m'
VERMELHO = '\033[91m'
RESET = '\033[0m'

def print_sucesso(msg):
    print(f"{VERDE}✅ {msg}{RESET}")

def print_info(msg):
    print(f"{AZUL}ℹ️  {msg}{RESET}")

def print_erro(msg):
    print(f"{VERMELHO}❌ {msg}{RESET}")

def separador():
    print(f"\n{AZUL}{'='*60}{RESET}\n")

# Dados de teste
USUARIOS = [
    {"email": "ana.silva@test.com", "senha": "senha123", "nome": "Ana Silva", "cidade": "São Paulo", "neurodiversidade": "TEA"},
    {"email": "carlos.santos@test.com", "senha": "senha123", "nome": "Carlos Santos", "cidade": "São Paulo", "neurodiversidade": "TDAH"},
    {"email": "maria.oliveira@test.com", "senha": "senha123", "nome": "Maria Oliveira", "cidade": "São Paulo", "neurodiversidade": "Outro"},
]

LOCAIS = [
    {"nome_local": "Starbucks Paulista", "endereco": "Avenida Paulista, 1000", "tipo_ambiente": "Cafeteria", "lat": -23.5615, "lon": -46.6561},
    {"nome_local": "Biblioteca Municipal", "endereco": "Rua dos Gusmões, 123", "tipo_ambiente": "Biblioteca", "lat": -23.5512, "lon": -46.6345},
    {"nome_local": "Shopping Imigrantes", "endereco": "Avenida Imigrantes, 1555", "tipo_ambiente": "Shopping", "lat": -23.6489, "lon": -46.5779},
    {"nome_local": "Restaurante Bella Italia", "endereco": "Rua da Consolação, 500", "tipo_ambiente": "Restaurante", "lat": -23.5545, "lon": -46.6559},
    {"nome_local": "Metrô Republica", "endereco": "Praça da República", "tipo_ambiente": "Transporte Público", "lat": -23.5497, "lon": -46.6349},
]

def registrar_usuario(usuario):
    """Registra um novo usuário"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/registro",
            json=usuario,
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            print_sucesso(f"Usuário registrado: {usuario['nome']} ({usuario['email']})")
            return usuario["email"]
        elif response.status_code == 400:
            print_info(f"Usuário já existe: {usuario['email']}")
            return usuario["email"]
        else:
            print_erro(f"Erro {response.status_code}: {response.text[:100]}")
            return None
    except Exception as e:
        print_erro(f"Exceção: {str(e)}")
        return None

def fazer_login(email, senha):
    """Faz login e retorna token"""
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
            print_erro(f"Erro ao fazer login: {response.text[:100]}")
            return None
    except Exception as e:
        print_erro(f"Exceção: {str(e)}")
        return None

def criar_registro(token, lugar_idx):
    """Cria um registro de medição"""
    try:
        local = LOCAIS[lugar_idx]
        
        # Gera dados realistas
        if local["tipo_ambiente"] == "Biblioteca":
            ruido_db = round(uniform(30, 45), 1)
            luminosidade_lux = round(uniform(200, 400), 1)
        elif local["tipo_ambiente"] == "Cafeteria":
            ruido_db = round(uniform(55, 70), 1)
            luminosidade_lux = round(uniform(300, 500), 1)
        elif local["tipo_ambiente"] == "Shopping":
            ruido_db = round(uniform(65, 80), 1)
            luminosidade_lux = round(uniform(500, 1000), 1)
        elif local["tipo_ambiente"] == "Restaurante":
            ruido_db = round(uniform(60, 75), 1)
            luminosidade_lux = round(uniform(200, 400), 1)
        elif local["tipo_ambiente"] == "Transporte Público":
            ruido_db = round(uniform(70, 85), 1)
            luminosidade_lux = round(uniform(100, 300), 1)
        else:
            ruido_db = round(uniform(50, 65), 1)
            luminosidade_lux = round(uniform(300, 600), 1)
        
        registro = {
            "place_id": f"place_{lugar_idx}_{int(time.time())}",
            "nome_local": local["nome_local"],
            "endereco": local["endereco"],
            "tipo_ambiente": local["tipo_ambiente"],
            "coordenadas": {"latitude": local["lat"], "longitude": local["lon"]},
            "ruido_db": ruido_db,
            "luminosidade_lux": luminosidade_lux
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/registros",
            json=registro,
            headers=headers,
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            print_sucesso(f"Registro criado: {local['nome_local']} ({ruido_db}dB, {luminosidade_lux}Lux)")
            return True
        else:
            print_erro(f"Erro {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print_erro(f"Exceção: {str(e)}")
        return False

def main():
    print(f"\n{AZUL}{'='*60}{RESET}")
    print(f"{VERDE}🌱 POPULANDO BANCO COM DADOS DE TESTE{RESET}")
    print(f"{AZUL}{'='*60}{RESET}\n")
    
    # Verifica API
    print_info("Verificando se a API está rodando...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print_erro("API não está respondendo corretamente")
            return
    except:
        print_erro("API não está disponível em http://localhost:8000")
        print_info("Inicie com: cd estrutura-back && python3 main.py")
        return
    
    print_sucesso("API respondendo!")
    
    # Etapa 1: Registrar usuários
    separador()
    print(f"{VERDE}ETAPA 1: Registrando usuários{RESET}\n")
    
    emails = []
    for usuario in USUARIOS:
        email = registrar_usuario(usuario)
        if email:
            emails.append(email)
        time.sleep(0.3)
    
    print_info(f"Total: {len(emails)} usuários\n")
    
    # Etapa 2: Criar registros
    separador()
    print(f"{VERDE}ETAPA 2: Criando registros de medições{RESET}\n")
    
    for email in emails:
        print_info(f"Login com {email}...")
        token = fazer_login(email, "senha123")
        
        if not token:
            continue
        
        print_sucesso("Token recebido!")
        
        # 2-3 registros por usuário
        num_registros = randint(2, 3)
        for _ in range(num_registros):
            lugar_idx = randint(0, len(LOCAIS) - 1)
            criar_registro(token, lugar_idx)
            time.sleep(0.2)
    
    # Status final
    separador()
    print(f"{VERDE}ETAPA 3: Verificando status final{RESET}\n")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  👥 Usuários: {data.get('usuarios_cadastrados', 0)}")
            print(f"  📍 Locais: {data.get('locais_cadastrados', 0)}")
            print(f"  📊 Registros: {data.get('registros_totais', 0)}")
    except:
        pass
    
    separador()
    print(f"{VERDE}✅ DADOS POPULADOS COM SUCESSO!{RESET}\n")
    print(f"{AZUL}Próximas ações:{RESET}")
    print(f"  1. Acesse http://localhost:3000")
    print(f"  2. Faça login com:")
    if emails:
        print(f"     Email: {emails[0]}")
        print(f"     Senha: senha123")
    print(f"  3. Explore os dados no mapa e tabelas\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{AMARELO}⏸️  Cancelado{RESET}\n")
    except Exception as e:
        print_erro(f"Erro: {str(e)}")
