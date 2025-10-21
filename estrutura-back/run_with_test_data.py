#!/usr/bin/env python3
"""
Script para rodar o servidor FastAPI com dados de teste pré-carregados.
"""

import sys
sys.path.insert(0, '/Users/kimgomes/Desktop/sensorial_app/estrutura-back')

from main import app, db_users, db_records, db_locations, create_access_token, hash_password
from datetime import datetime, timedelta
from random import choice, randint, uniform
import uvicorn

print("\n" + "="*70)
print("🌱 CARREGANDO DADOS DE TESTE E INICIANDO SERVIDOR")
print("="*70 + "\n")

# ============================================================================
# CRIAR DADOS DE TESTE
# ============================================================================

print("📝 Criando dados de teste...\n")

# Usuários
usuarios = [
    {
        "email": "ana@test.com",
        "senha": "123456",
        "nome": "Ana Silva",
        "cidade": "São Paulo",
        "neurodiversidade": "TEA"
    },
    {
        "email": "carlos@test.com",
        "senha": "123456",
        "nome": "Carlos Santos",
        "cidade": "São Paulo",
        "neurodiversidade": "TDAH"
    },
    {
        "email": "maria@test.com",
        "senha": "123456",
        "nome": "Maria Oliveira",
        "cidade": "São Paulo",
        "neurodiversidade": "Outro"
    }
]

for usuario in usuarios:
    if usuario["email"] not in db_users:
        db_users[usuario["email"]] = {
            "nome": usuario["nome"],
            "email": usuario["email"],
            "senha_hash": hash_password(usuario["senha"]),
            "cidade": usuario["cidade"],
            "neurodiversidade": usuario["neurodiversidade"],
            "data_criacao": datetime.now()
        }
        print(f"✅ {usuario['nome']}")

# Locais
locais_dados = [
    {"nome": "Starbucks Paulista", "endereco": "Avenida Paulista, 1000", "tipo": "Cafeteria", "lat": -23.5615, "lon": -46.6561},
    {"nome": "Biblioteca Municipal", "endereco": "Rua dos Gusmões, 123", "tipo": "Biblioteca", "lat": -23.5512, "lon": -46.6345},
    {"nome": "Shopping Imigrantes", "endereco": "Avenida Imigrantes, 1555", "tipo": "Shopping", "lat": -23.6489, "lon": -46.5779},
    {"nome": "Restaurante Bella Italia", "endereco": "Rua da Consolação, 500", "tipo": "Restaurante", "lat": -23.5545, "lon": -46.6559},
    {"nome": "Metrô República", "endereco": "Praça da República", "tipo": "Transporte Público", "lat": -23.5497, "lon": -46.6349},
]

for idx, local_dados in enumerate(locais_dados):
    place_id = f"place_{idx}"
    if place_id not in db_locations:
        db_locations[place_id] = {
            "place_id": place_id,
            "nome_local": local_dados["nome"],
            "endereco": local_dados["endereco"],
            "tipo_ambiente": local_dados["tipo"],
            "coordenadas": {"latitude": local_dados["lat"], "longitude": local_dados["lon"]},
            "data_criacao": datetime.now()
        }
        print(f"📍 {local_dados['nome']}")

# Registros de medições
registros_dados = [
    {"place_id": "place_0", "nome": "Starbucks Paulista", "ruido": 62.5, "lux": 380.0},
    {"place_id": "place_1", "nome": "Biblioteca Municipal", "ruido": 38.0, "lux": 320.0},
    {"place_id": "place_2", "nome": "Shopping Imigrantes", "ruido": 72.0, "lux": 650.0},
    {"place_id": "place_3", "nome": "Restaurante Bella Italia", "ruido": 68.5, "lux": 280.0},
    {"place_id": "place_4", "nome": "Metrô República", "ruido": 78.0, "lux": 200.0},
    {"place_id": "place_0", "nome": "Starbucks Paulista", "ruido": 58.5, "lux": 390.0},
    {"place_id": "place_1", "nome": "Biblioteca Municipal", "ruido": 37.5, "lux": 330.0},
]

def classificar(valor, tipo="ruido"):
    """Classifica valor como Bom/Ok/Atenção/Ruim"""
    if tipo == "ruido":
        if valor < 45:
            return "Bom"
        elif valor < 55:
            return "Ok"
        elif valor < 65:
            return "Atenção"
        else:
            return "Ruim"
    else:  # luz
        if valor > 300:
            return "Bom"
        elif valor > 200:
            return "Ok"
        elif valor > 100:
            return "Atenção"
        else:
            return "Ruim"

import uuid
for idx, reg_dados in enumerate(registros_dados):
    db_records.append({
        "id": str(uuid.uuid4()),
        "place_id": reg_dados["place_id"],
        "usuario_email": usuarios[idx % len(usuarios)]["email"],
        "timestamp": datetime.now() - timedelta(days=randint(0, 15)),
        "ruido_db": reg_dados["ruido"],
        "luminosidade_lux": reg_dados["lux"],
        "nivel_ruido": classificar(reg_dados["ruido"], "ruido"),
        "nivel_luz": classificar(reg_dados["lux"], "luz"),
        "tipo_medida": "sensor"
    })

print(f"\n📊 Dados criados:")
print(f"   👥 Usuários: {len(db_users)}")
print(f"   📍 Locais: {len(db_locations)}")
print(f"   📈 Registros: {len(db_records)}\n")

print("="*70)
print("🚀 INICIANDO SERVIDOR FASTAPI")
print("="*70 + "\n")

print(f"📱 Acesse: http://localhost:8000")
print(f"📚 Documentação: http://localhost:8000/docs")
print(f"🎨 Frontend: http://localhost:3000\n")

print(f"Login com:")
print(f"  Email: ana@test.com")
print(f"  Senha: 123456\n")

print("="*70 + "\n")

# Iniciar servidor
uvicorn.run(app, host="0.0.0.0", port=8000)
