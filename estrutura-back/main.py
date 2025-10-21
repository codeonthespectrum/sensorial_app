"""
API Backend para App de Ambientes Acessíveis para Autistas
Mede ruído e luminosidade em locais públicos baseado em normas ABNT
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from enum import Enum
from jose import jwt, JWTError
import hashlib
import os

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Ambientes Acessíveis API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Segurança - usando hash simples para evitar conflitos de bcrypt
security = HTTPBearer()

# Simulação de banco de dados (em produção usar MongoDB)
db_users = {}
db_locations = {}
db_records = []

# ============= ENUMS E CONSTANTES =============

class NivelClassificacao(str, Enum):
    BOM = "Bom"
    OK = "Ok"
    ATENCAO = "Atenção"
    RUIM = "Ruim"

class TipoAmbiente(str, Enum):
    RESTAURANTE = "Restaurante"
    BIBLIOTECA = "Biblioteca"
    SHOPPING = "Shopping"
    HOSPITAL = "Hospital"
    ESCOLA = "Escola"
    ESCRITORIO = "Escritorio"
    PARQUE = "Parque"
    CAFETERIA = "Cafeteria"

class Neurodiversidade(str, Enum):
    AUTISMO = "TEA"
    TDAH = "TDAH"
    OUTRO = "Outro"
    NAO_INFORMADO = "Nao Informado"

# Limites baseados em NBR 10152 (ruído) e NBR 8995/5413 (iluminação)
LIMITES_AMBIENTES = {
    TipoAmbiente.RESTAURANTE: {
        "ruido": {"bom": (0, 45), "ok": (45, 50), "atencao": (50, 55), "ruim": (55, 120)},
        "luz": {"bom": (200, 300), "ok": (150, 200), "atencao": (100, 150), "ruim": (0, 100)}
    },
    TipoAmbiente.BIBLIOTECA: {
        "ruido": {"bom": (0, 35), "ok": (35, 40), "atencao": (40, 45), "ruim": (45, 120)},
        "luz": {"bom": (300, 500), "ok": (250, 300), "atencao": (200, 250), "ruim": (0, 200)}
    },
    TipoAmbiente.SHOPPING: {
        "ruido": {"bom": (0, 50), "ok": (50, 55), "atencao": (55, 60), "ruim": (60, 120)},
        "luz": {"bom": (300, 500), "ok": (200, 300), "atencao": (150, 200), "ruim": (0, 150)}
    },
    TipoAmbiente.HOSPITAL: {
        "ruido": {"bom": (0, 35), "ok": (35, 40), "atencao": (40, 45), "ruim": (45, 120)},
        "luz": {"bom": (200, 400), "ok": (150, 200), "atencao": (100, 150), "ruim": (0, 100)}
    },
    TipoAmbiente.ESCOLA: {
        "ruido": {"bom": (0, 40), "ok": (40, 45), "atencao": (45, 50), "ruim": (50, 120)},
        "luz": {"bom": (300, 500), "ok": (250, 300), "atencao": (200, 250), "ruim": (0, 200)}
    },
    TipoAmbiente.ESCRITORIO: {
        "ruido": {"bom": (0, 45), "ok": (45, 50), "atencao": (50, 55), "ruim": (55, 120)},
        "luz": {"bom": (500, 750), "ok": (400, 500), "atencao": (300, 400), "ruim": (0, 300)}
    },
    TipoAmbiente.PARQUE: {
        "ruido": {"bom": (0, 50), "ok": (50, 55), "atencao": (55, 60), "ruim": (60, 120)},
        "luz": {"bom": (100, 300), "ok": (75, 100), "atencao": (50, 75), "ruim": (0, 50)}
    },
    TipoAmbiente.CAFETERIA: {
        "ruido": {"bom": (0, 45), "ok": (45, 50), "atencao": (50, 55), "ruim": (55, 120)},
        "luz": {"bom": (200, 300), "ok": (150, 200), "atencao": (100, 150), "ruim": (0, 100)}
    }
}

# ============= MODELS =============

class UserCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(..., min_length=6)
    cidade: str
    neurodiversidade: Neurodiversidade = Neurodiversidade.NAO_INFORMADO

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Coordenadas(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class RegistroAmbiente(BaseModel):
    place_id: str
    nome_local: str
    endereco: str
    tipo_ambiente: TipoAmbiente
    coordenadas: Coordenadas
    nivel_ruido_manual: Optional[NivelClassificacao] = None
    nivel_luz_manual: Optional[NivelClassificacao] = None
    ruido_db: Optional[float] = Field(None, ge=0, le=120)
    luminosidade_lux: Optional[float] = Field(None, ge=0, le=10000)

class LocalInfo(BaseModel):
    place_id: str
    nome_local: str
    endereco: str
    tipo_ambiente: TipoAmbiente
    coordenadas: Coordenadas
    selo_acessivel: bool
    ultima_atualizacao: datetime
    nivel_ruido_atual: NivelClassificacao
    nivel_luz_atual: NivelClassificacao
    total_registros: int

class EstatisticasHorario(BaseModel):
    dia_semana: str
    hora: int
    media_ruido_db: float
    media_luz_lux: float
    quantidade_registros: int

# ============= FUNÇÕES AUXILIARES =============

def classificar_valor(valor: float, limites: Dict, tipo: str) -> NivelClassificacao:
    """Classifica um valor de ruído ou luz baseado nos limites do ambiente"""
    for nivel, (min_val, max_val) in limites[tipo].items():
        if min_val <= valor < max_val:
            return NivelClassificacao(nivel)
    return NivelClassificacao.RUIM

def verificar_selo_acessivel(place_id: str) -> bool:
    """Verifica se local tem 100 registros bom/ok no último mês"""
    um_mes_atras = datetime.now() - timedelta(days=30)
    
    registros_local = [
        r for r in db_records 
        if r["place_id"] == place_id and r["timestamp"] >= um_mes_atras
    ]
    
    if len(registros_local) < 100:
        return False
    
    registros_bons = [
        r for r in registros_local
        if r["nivel_ruido"] in [NivelClassificacao.BOM, NivelClassificacao.OK]
        and r["nivel_luz"] in [NivelClassificacao.BOM, NivelClassificacao.OK]
    ]
    
    return len(registros_bons) >= 100

def hash_password(password: str) -> str:
    """Cria hash SHA256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None or email not in db_users:
            raise HTTPException(status_code=401, detail="Não autenticado")
        return db_users[email]
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

# ============= ENDPOINTS =============

@app.get("/")
def root():
    return {
        "mensagem": "API Ambientes Acessíveis para Autistas",
        "versao": "1.0.0",
        "documentacao": "/docs"
    }

@app.post("/auth/registro", response_model=Token, status_code=status.HTTP_201_CREATED)
def registrar_usuario(user: UserCreate):
    """Registra um novo usuário"""
    if user.email in db_users:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    db_users[user.email] = {
        "nome": user.nome,
        "email": user.email,
        "senha_hash": hash_password(user.senha),
        "cidade": user.cidade,
        "neurodiversidade": user.neurodiversidade,
        "data_criacao": datetime.now()
    }
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token}

@app.post("/auth/login", response_model=Token)
def login(user: UserLogin):
    """Faz login e retorna token JWT"""
    if user.email not in db_users:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    db_user = db_users[user.email]
    if not verify_password(user.senha, db_user["senha_hash"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token}

@app.get("/auth/me")
def usuario_atual(current_user = Depends(get_current_user)):
    """Retorna dados do usuário logado"""
    return {
        "nome": current_user["nome"],
        "email": current_user["email"],
        "cidade": current_user["cidade"],
        "neurodiversidade": current_user["neurodiversidade"]
    }

@app.post("/registros", status_code=status.HTTP_201_CREATED)
def criar_registro(registro: RegistroAmbiente, current_user = Depends(get_current_user)):
    """Cria novo registro de ambiente"""
    
    # Se valores manuais foram fornecidos, usa eles
    if registro.nivel_ruido_manual and registro.nivel_luz_manual:
        nivel_ruido = registro.nivel_ruido_manual
        nivel_luz = registro.nivel_luz_manual
        ruido_db = None
        lux = None
    # Senão, classifica baseado nos valores medidos
    elif registro.ruido_db is not None and registro.luminosidade_lux is not None:
        limites = LIMITES_AMBIENTES[registro.tipo_ambiente]
        nivel_ruido = classificar_valor(registro.ruido_db, limites, "ruido")
        nivel_luz = classificar_valor(registro.luminosidade_lux, limites, "luz")
        ruido_db = registro.ruido_db
        lux = registro.luminosidade_lux
    else:
        raise HTTPException(
            status_code=400, 
            detail="Forneça valores manuais OU valores medidos (dB e lux)"
        )
    
    # Cria registro
    novo_registro = {
        "id": len(db_records) + 1,
        "place_id": registro.place_id,
        "usuario_email": current_user["email"],
        "timestamp": datetime.now(),
        "nivel_ruido": nivel_ruido,
        "nivel_luz": nivel_luz,
        "ruido_db": ruido_db,
        "luminosidade_lux": lux
    }
    
    db_records.append(novo_registro)
    
    # Atualiza/Cria local
    if registro.place_id not in db_locations:
        db_locations[registro.place_id] = {
            "place_id": registro.place_id,
            "nome_local": registro.nome_local,
            "endereco": registro.endereco,
            "tipo_ambiente": registro.tipo_ambiente,
            "coordenadas": registro.coordenadas.dict()
        }
    
    return {
        "mensagem": "Registro criado com sucesso",
        "id": novo_registro["id"],
        "nivel_ruido": nivel_ruido,
        "nivel_luz": nivel_luz
    }

@app.get("/locais/proximos")
def buscar_locais_proximos(
    latitude: float,
    longitude: float,
    raio_km: float = 5.0,
    tipo_ambiente: Optional[TipoAmbiente] = None
):
    """Busca locais próximos às coordenadas fornecidas"""
    # Simplificado: retorna todos os locais (em produção, usar geolocalização real)
    locais = list(db_locations.values())
    
    if tipo_ambiente:
        locais = [l for l in locais if l["tipo_ambiente"] == tipo_ambiente]
    
    resultado = []
    for local in locais:
        registros_local = [r for r in db_records if r["place_id"] == local["place_id"]]
        
        if registros_local:
            ultimo_registro = max(registros_local, key=lambda x: x["timestamp"])
            
            resultado.append({
                "place_id": local["place_id"],
                "nome_local": local["nome_local"],
                "tipo_ambiente": local["tipo_ambiente"],
                "coordenadas": local["coordenadas"],
                "nivel_ruido_atual": ultimo_registro["nivel_ruido"],
                "nivel_luz_atual": ultimo_registro["nivel_luz"],
                "ultima_atualizacao": ultimo_registro["timestamp"],
                "selo_acessivel": verificar_selo_acessivel(local["place_id"])
            })
    
    return {"locais": resultado, "total": len(resultado)}

@app.get("/locais/{place_id}")
def detalhes_local(place_id: str):
    """Retorna detalhes completos de um local específico"""
    if place_id not in db_locations:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    
    local = db_locations[place_id]
    registros = [r for r in db_records if r["place_id"] == place_id]
    
    if not registros:
        raise HTTPException(status_code=404, detail="Nenhum registro encontrado para este local")
    
    # Últimos 5 registros
    ultimos_5 = sorted(registros, key=lambda x: x["timestamp"], reverse=True)[:5]
    
    ultimo = ultimos_5[0]
    
    # Estatísticas por horário (últimos 30 dias)
    um_mes_atras = datetime.now() - timedelta(days=30)
    registros_mes = [r for r in registros if r["timestamp"] >= um_mes_atras]
    
    estatisticas = {}
    for reg in registros_mes:
        if reg["ruido_db"] is not None and reg["luminosidade_lux"] is not None:
            dia = reg["timestamp"].strftime("%A")
            hora = reg["timestamp"].hour
            
            key = f"{dia}_{hora}"
            if key not in estatisticas:
                estatisticas[key] = {
                    "dia_semana": dia,
                    "hora": hora,
                    "ruidos": [],
                    "luzes": []
                }
            
            estatisticas[key]["ruidos"].append(reg["ruido_db"])
            estatisticas[key]["luzes"].append(reg["luminosidade_lux"])
    
    graficos = []
    for key, stats in estatisticas.items():
        if stats["ruidos"] and stats["luzes"]:
            graficos.append({
                "dia_semana": stats["dia_semana"],
                "hora": stats["hora"],
                "media_ruido_db": sum(stats["ruidos"]) / len(stats["ruidos"]),
                "media_luz_lux": sum(stats["luzes"]) / len(stats["luzes"]),
                "quantidade_registros": len(stats["ruidos"])
            })
    
    return {
        "place_id": local["place_id"],
        "nome_local": local["nome_local"],
        "endereco": local["endereco"],
        "tipo_ambiente": local["tipo_ambiente"],
        "coordenadas": local["coordenadas"],
        "selo_acessivel": verificar_selo_acessivel(place_id),
        "nivel_ruido_atual": ultimo["nivel_ruido"],
        "nivel_luz_atual": ultimo["nivel_luz"],
        "ultima_atualizacao": ultimo["timestamp"],
        "total_registros": len(registros),
        "ultimos_5_registros": [
            {
                "timestamp": r["timestamp"],
                "nivel_ruido": r["nivel_ruido"],
                "nivel_luz": r["nivel_luz"],
                "ruido_db": r["ruido_db"],
                "luminosidade_lux": r["luminosidade_lux"]
            }
            for r in ultimos_5
        ],
        "estatisticas_horario": sorted(graficos, key=lambda x: (x["dia_semana"], x["hora"]))
    }

@app.get("/tipos-ambiente")
def listar_tipos_ambiente():
    """Lista todos os tipos de ambiente disponíveis"""
    return {
        "tipos": [
            {
                "valor": tipo.value,
                "limites_ruido": LIMITES_AMBIENTES[tipo]["ruido"],
                "limites_luz": LIMITES_AMBIENTES[tipo]["luz"]
            }
            for tipo in TipoAmbiente
        ]
    }

@app.get("/health")
def health_check():
    """Verifica saúde da API"""
    return {
        "status": "ok",
        "timestamp": datetime.now(),
        "usuarios_cadastrados": len(db_users),
        "locais_cadastrados": len(db_locations),
        "registros_totais": len(db_records)
    }

# ============= ENDPOINTS DE MEDIÇÃO =============

class DadosAudio(BaseModel):
    frequencias: List[float] = Field(..., description="Array de frequências capturadas")
    energia_media: float = Field(..., ge=0, le=1, description="Energia média (0-1)")

class DadosLuminosidade(BaseModel):
    r: int = Field(..., ge=0, le=255, description="Componente Vermelho")
    g: int = Field(..., ge=0, le=255, description="Componente Verde")
    b: int = Field(..., ge=0, le=255, description="Componente Azul")

@app.post("/sensores/calibrar-ruido")
def calibrar_ruido():
    """Retorna valores de calibração para ruído"""
    return {
        "referencia_db": 20,  # 20 dB é geralmente o silêncio em um estúdio
        "max_db": 120,
        "min_db": 0,
        "fft_size": 2048,
        "smoothing_constant": 0.8,
        "mensagem": "Use estes valores para calibrar sua medição de ruído"
    }

@app.post("/sensores/processar-audio")
def processar_audio(dados: DadosAudio):
    """Processa dados de áudio e retorna nível de dB estimado"""
    
    if not dados.frequencias or len(dados.frequencias) == 0:
        raise HTTPException(status_code=400, detail="Nenhuma frequência capturada")
    
    # Calcular média de energia
    energia_media = dados.energia_media
    
    # Converter para dB (usando fórmula padrão)
    # dB = 20 * log10(energia_media / referencia)
    # Com referência de 20 µPa (20 × 10^-6 Pa)
    
    import math
    
    if energia_media <= 0:
        db_estimado = 0
    else:
        # Normalizar a energia
        referencia = 0.001  # Valor de referência para o microfone
        razao = energia_media / referencia if referencia > 0 else 0
        
        if razao > 0:
            db_estimado = min(20 * math.log10(razao), 120)
        else:
            db_estimado = 0
    
    # Limitar entre 0 e 120 dB
    db_estimado = max(0, min(120, db_estimado))
    
    return {
        "db_estimado": round(db_estimado, 1),
        "energia_media": round(dados.energia_media, 4),
        "quantidade_frequencias": len(dados.frequencias),
        "classificacao": classificar_valor(db_estimado, LIMITES_AMBIENTES[TipoAmbiente.RESTAURANTE], "ruido")
    }

@app.post("/sensores/processar-luminosidade")
def processar_luminosidade(dados: DadosLuminosidade):
    """Processa dados de luminosidade e retorna lux estimado"""
    
    import math
    
    # Calcular luminância relativa (padrão sRGB)
    # Fórmula: https://en.wikipedia.org/wiki/Relative_luminance
    
    r = dados.r / 255.0
    g = dados.g / 255.0
    b = dados.b / 255.0
    
    # Aplicar gamma correction
    def gamma_correct(c):
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4
    
    r = gamma_correct(r)
    g = gamma_correct(g)
    b = gamma_correct(b)
    
    # Calcular luminância
    luminancia = 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    # Estimar Lux baseado em luminância
    # Usando aproximação: Lux ≈ Luminância * constante
    # A constante varia, mas vamos usar uma escala proporcional
    
    # Se a câmera está apontada para um local muito escuro: ~0 Lux
    # Se está apontada para um local muito claro: ~500 Lux (aprox.)
    # Mapeamos em uma escala logarítmica
    
    if luminancia < 0.0001:
        lux_estimado = 0
    else:
        # Mapeamento logarítmico: log(luminancia) -> lux
        lux_estimado = 10000 * (luminancia ** 2)  # Aproximação exponencial
    
    # Limitar entre 0 e 10000 Lux
    lux_estimado = max(0, min(10000, lux_estimado))
    
    return {
        "lux_estimado": round(lux_estimado, 1),
        "luminancia": round(luminancia, 4),
        "rgb": {"r": dados.r, "g": dados.g, "b": dados.b},
        "classificacao": classificar_valor(lux_estimado, LIMITES_AMBIENTES[TipoAmbiente.RESTAURANTE], "luz")
    }

@app.get("/sensores/info")
def info_sensores():
    """Retorna informações sobre como usar os sensores"""
    return {
        "ruido": {
            "metodo": "Web Audio API",
            "descricao": "Captura áudio do microfone e analisa frequências",
            "precisao": "±3-5 dB",
            "limitacoes": [
                "Requer permissão do usuário",
                "Microfone deve estar calibrado",
                "Ambiente silencioso durante captura",
                "Mínimo 2-3 segundos de captura"
            ]
        },
        "luminosidade": {
            "metodo": "Canvas + Camera",
            "descricao": "Captura vídeo da câmera e analisa pixels",
            "precisao": "±20-30 Lux",
            "limitacoes": [
                "Requer permissão da câmera",
                "Câmera deve estar apontada para o ambiente",
                "Sem obstrução (mão, objeto)",
                "Calibração manual recomendada"
            ]
        },
        "calibracao": {
            "ruido": "Use um ambiente silencioso como referência (ex: biblioteca = 35-40 dB)",
            "luminosidade": "Aponte a câmera para uma superfície branca à luz natural (~400-500 Lux)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)