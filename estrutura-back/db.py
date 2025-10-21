"""
Configuração do MongoDB para produção
Substitua os dicionários em memória do main.py por estas funções
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, GEOSPHERE
from datetime import datetime, timedelta
import os
from typing import Optional, List, Dict

# Configuração
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ambientes_acessiveis")

# Cliente MongoDB
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

# Coleções
users_collection = db["users"]
locations_collection = db["locations"]
records_collection = db["records"]

async def init_db():
    """Inicializa índices do banco de dados"""
    
    # Índices para usuários
    await users_collection.create_index([("email", ASCENDING)], unique=True)
    
    # Índices para locais (geoespacial)
    await locations_collection.create_index([("place_id", ASCENDING)], unique=True)
    await locations_collection.create_index([("coordenadas", GEOSPHERE)])
    await locations_collection.create_index([("tipo_ambiente", ASCENDING)])
    
    # Índices para registros
    await records_collection.create_index([("place_id", ASCENDING), ("timestamp", DESCENDING)])
    await records_collection.create_index([("timestamp", DESCENDING)])
    await records_collection.create_index([("usuario_email", ASCENDING)])
    
    print("✅ Índices do MongoDB criados com sucesso!")

# ============= FUNÇÕES DE USUÁRIOS =============

async def criar_usuario(usuario_data: dict) -> dict:
    """Cria um novo usuário"""
    usuario_data["data_criacao"] = datetime.now()
    result = await users_collection.insert_one(usuario_data)
    usuario_data["_id"] = str(result.inserted_id)
    return usuario_data

async def buscar_usuario_por_email(email: str) -> Optional[dict]:
    """Busca usuário por email"""
    user = await users_collection.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
    return user

async def atualizar_usuario(email: str, dados: dict) -> bool:
    """Atualiza dados do usuário"""
    result = await users_collection.update_one(
        {"email": email},
        {"$set": dados}
    )
    return result.modified_count > 0

# ============= FUNÇÕES DE LOCAIS =============

async def criar_ou_atualizar_local(local_data: dict) -> dict:
    """Cria ou atualiza um local"""
    # Converte coordenadas para formato GeoJSON
    if "coordenadas" in local_data and "latitude" in local_data["coordenadas"]:
        local_data["coordenadas"] = {
            "type": "Point",
            "coordinates": [
                local_data["coordenadas"]["longitude"],
                local_data["coordenadas"]["latitude"]
            ]
        }
    
    result = await locations_collection.update_one(
        {"place_id": local_data["place_id"]},
        {"$set": local_data},
        upsert=True
    )
    
    return local_data

async def buscar_local_por_id(place_id: str) -> Optional[dict]:
    """Busca local por place_id"""
    local = await locations_collection.find_one({"place_id": place_id})
    
    if local:
        local["_id"] = str(local["_id"])
        # Converte coordenadas de volta para formato simples
        if "coordenadas" in local and "coordinates" in local["coordenadas"]:
            coords = local["coordenadas"]["coordinates"]
            local["coordenadas"] = {
                "longitude": coords[0],
                "latitude": coords[1]
            }
    
    return local

async def buscar_locais_proximos(
    latitude: float,
    longitude: float,
    raio_metros: float = 5000,
    tipo_ambiente: Optional[str] = None
) -> List[dict]:
    """Busca locais próximos usando índice geoespacial"""
    
    query = {
        "coordenadas": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": raio_metros
            }
        }
    }
    
    if tipo_ambiente:
        query["tipo_ambiente"] = tipo_ambiente
    
    cursor = locations_collection.find(query).limit(50)
    locais = await cursor.to_list(length=50)
    
    # Converte coordenadas
    for local in locais:
        local["_id"] = str(local["_id"])
        if "coordenadas" in local and "coordinates" in local["coordenadas"]:
            coords = local["coordenadas"]["coordinates"]
            local["coordenadas"] = {
                "longitude": coords[0],
                "latitude": coords[1]
            }
    
    return locais

# ============= FUNÇÕES DE REGISTROS =============

async def criar_registro(registro_data: dict) -> dict:
    """Cria um novo registro"""
    registro_data["timestamp"] = datetime.now()
    result = await records_collection.insert_one(registro_data)
    registro_data["_id"] = str(result.inserted_id)
    return registro_data

async def buscar_registros_local(
    place_id: str,
    limit: Optional[int] = None,
    data_inicio: Optional[datetime] = None
) -> List[dict]:
    """Busca registros de um local"""
    
    query = {"place_id": place_id}
    
    if data_inicio:
        query["timestamp"] = {"$gte": data_inicio}
    
    cursor = records_collection.find(query).sort("timestamp", DESCENDING)
    
    if limit:
        cursor = cursor.limit(limit)
    
    registros = await cursor.to_list(length=limit or 1000)
    
    for registro in registros:
        registro["_id"] = str(registro["_id"])
    
    return registros

async def contar_registros_bons(place_id: str, dias: int = 30) -> int:
    """Conta registros bom/ok no período"""
    data_inicio = datetime.now() - timedelta(days=dias)
    
    count = await records_collection.count_documents({
        "place_id": place_id,
        "timestamp": {"$gte": data_inicio},
        "nivel_ruido": {"$in": ["bom", "ok"]},
        "nivel_luz": {"$in": ["bom", "ok"]}
    })
    
    return count

async def buscar_ultimo_registro(place_id: str) -> Optional[dict]:
    """Busca o último registro de um local"""
    registro = await records_collection.find_one(
        {"place_id": place_id},
        sort=[("timestamp", DESCENDING)]
    )
    
    if registro:
        registro["_id"] = str(registro["_id"])
    
    return registro

async def buscar_estatisticas_horario(place_id: str, dias: int = 30) -> List[dict]:
    """Gera estatísticas por horário/dia usando agregação"""
    data_inicio = datetime.now() - timedelta(days=dias)
    
    pipeline = [
        {
            "$match": {
                "place_id": place_id,
                "timestamp": {"$gte": data_inicio},
                "ruido_db": {"$ne": None},
                "luminosidade_lux": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": {
                    "dia_semana": {"$dayOfWeek": "$timestamp"},
                    "hora": {"$hour": "$timestamp"}
                },
                "media_ruido_db": {"$avg": "$ruido_db"},
                "media_luz_lux": {"$avg": "$luminosidade_lux"},
                "quantidade_registros": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "dia_semana": "$_id.dia_semana",
                "hora": "$_id.hora",
                "media_ruido_db": {"$round": ["$media_ruido_db", 1]},
                "media_luz_lux": {"$round": ["$media_luz_lux", 1]},
                "quantidade_registros": 1
            }
        },
        {
            "$sort": {"dia_semana": 1, "hora": 1}
        }
    ]
    
    cursor = records_collection.aggregate(pipeline)
    estatisticas = await cursor.to_list(length=None)
    
    # Converte número do dia para nome
    dias_semana = {
        1: "Domingo",
        2: "Segunda",
        3: "Terça",
        4: "Quarta",
        5: "Quinta",
        6: "Sexta",
        7: "Sábado"
    }
    
    for stat in estatisticas:
        stat["dia_semana"] = dias_semana.get(stat["dia_semana"], "Desconhecido")
    
    return estatisticas

async def buscar_total_registros() -> int:
    """Retorna total de registros no sistema"""
    return await records_collection.count_documents({})

async def buscar_total_locais() -> int:
    """Retorna total de locais cadastrados"""
    return await locations_collection.count_documents({})

async def buscar_total_usuarios() -> int:
    """Retorna total de usuários"""
    return await users_collection.count_documents({})

# ============= FUNÇÕES DE LIMPEZA =============

async def limpar_registros_antigos(dias: int = 90):
    """Remove registros mais antigos que X dias"""
    data_limite = datetime.now() - timedelta(days=dias)
    
    result = await records_collection.delete_many({
        "timestamp": {"$lt": data_limite}
    })
    
    return result.deleted_count

async def limpar_locais_sem_registros():
    """Remove locais que não têm nenhum registro"""
    
    # Busca todos place_ids com registros
    pipeline = [
        {"$group": {"_id": "$place_id"}},
        {"$project": {"place_id": "$_id", "_id": 0}}
    ]
    
    cursor = records_collection.aggregate(pipeline)
    places_com_registros = [doc["place_id"] async for doc in cursor]
    
    # Remove locais sem registros
    result = await locations_collection.delete_many({
        "place_id": {"$nin": places_com_registros}
    })
    
    return result.deleted_count

# ============= HEALTH CHECK =============

async def verificar_conexao() -> bool:
    """Verifica se a conexão com MongoDB está ativa"""
    try:
        await client.admin.command('ping')
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar no MongoDB: {e}")
        return False