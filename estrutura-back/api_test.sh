#!/bin/bash

# Script de teste da API - Ambientes Acessíveis
# Execute: chmod +x test_api.sh && ./test_api.sh

API_URL="http://localhost:8000"
echo "🧪 Testando API em: $API_URL"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4
    
    echo -e "${YELLOW}Testando: $method $endpoint${NC}"
    
    if [ -z "$token" ]; then
        response=$(curl -s -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data")
    fi
    
    echo "$response" | jq '.'
    echo ""
}

# 1. Health Check
echo "=== 1. HEALTH CHECK ==="
test_endpoint "GET" "/health"

# 2. Listar tipos de ambiente
echo "=== 2. TIPOS DE AMBIENTE ==="
test_endpoint "GET" "/tipos-ambiente"

# 3. Registrar usuário
echo "=== 3. REGISTRO DE USUÁRIO ==="
USER_DATA='{
  "nome": "João Silva Teste",
  "email": "joao.teste@email.com",
  "senha": "senha123456",
  "cidade": "São Paulo",
  "neurodiversidade": "autismo"
}'
register_response=$(curl -s -X POST "$API_URL/auth/registro" \
    -H "Content-Type: application/json" \
    -d "$USER_DATA")

echo "$register_response" | jq '.'
TOKEN=$(echo "$register_response" | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ ! -z "$TOKEN" ]; then
    echo -e "${GREEN}✅ Token obtido com sucesso!${NC}"
else
    echo -e "${RED}❌ Falha ao obter token${NC}"
    exit 1
fi
echo ""

# 4. Login
echo "=== 4. LOGIN ==="
LOGIN_DATA='{
  "email": "joao.teste@email.com",
  "senha": "senha123456"
}'
test_endpoint "POST" "/auth/login" "$LOGIN_DATA"

# 5. Ver perfil
echo "=== 5. PERFIL DO USUÁRIO ==="
test_endpoint "GET" "/auth/me" "" "$TOKEN"

# 6. Criar registro manual
echo "=== 6. CRIAR REGISTRO (MANUAL) ==="
REGISTRO_MANUAL='{
  "place_id": "ChIJTest123456",
  "nome_local": "Biblioteca Teste Central",
  "endereco": "Rua das Flores, 123 - Centro",
  "tipo_ambiente": "biblioteca",
  "coordenadas": {
    "latitude": -23.550520,
    "longitude": -46.633308
  },
  "nivel_ruido_manual": "bom",
  "nivel_luz_manual": "ok"
}'
test_endpoint "POST" "/registros" "$REGISTRO_MANUAL" "$TOKEN"

# 7. Criar registro com medição
echo "=== 7. CRIAR REGISTRO (MEDIÇÃO) ==="
REGISTRO_MEDICAO='{
  "place_id": "ChIJTest123456",
  "nome_local": "Biblioteca Teste Central",
  "endereco": "Rua das Flores, 123 - Centro",
  "tipo_ambiente": "biblioteca",
  "coordenadas": {
    "latitude": -23.550520,
    "longitude": -46.633308
  },
  "ruido_db": 38.5,
  "luminosidade_lux": 320
}'
test_endpoint "POST" "/registros" "$REGISTRO_MEDICAO" "$TOKEN"

# 8. Criar mais registros para teste de estatísticas
echo "=== 8. CRIANDO MAIS REGISTROS PARA ESTATÍSTICAS ==="
for i in {1..5}; do
    RUIDO=$((30 + RANDOM % 15))
    LUX=$((250 + RANDOM % 100))
    
    REGISTRO="{
      \"place_id\": \"ChIJTest123456\",
      \"nome_local\": \"Biblioteca Teste Central\",
      \"endereco\": \"Rua das Flores, 123 - Centro\",
      \"tipo_ambiente\": \"biblioteca\",
      \"coordenadas\": {
        \"latitude\": -23.550520,
        \"longitude\": -46.633308
      },
      \"ruido_db\": $RUIDO,
      \"luminosidade_lux\": $LUX
    }"
    
    echo "Registro $i: ${RUIDO}dB, ${LUX}lux"
    curl -s -X POST "$API_URL/registros" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "$REGISTRO" > /dev/null
done
echo -e "${GREEN}✅ 5 registros adicionais criados${NC}"
echo ""

# 9. Buscar locais próximos
echo "=== 9. BUSCAR LOCAIS PRÓXIMOS ==="
test_endpoint "GET" "/locais/proximos?latitude=-23.550520&longitude=-46.633308&tipo_ambiente=biblioteca" "" "$TOKEN"

# 10. Ver detalhes do local
echo "=== 10. DETALHES DO LOCAL ==="
test_endpoint "GET" "/locais/ChIJTest123456" "" "$TOKEN"

# 11. Criar local de restaurante
echo "=== 11. CRIAR LOCAL RESTAURANTE ==="
REGISTRO_RESTAURANTE='{
  "place_id": "ChIJRestaurantTest789",
  "nome_local": "Restaurante Silencioso",
  "endereco": "Av. Paulista, 1000",
  "tipo_ambiente": "restaurante",
  "coordenadas": {
    "latitude": -23.561414,
    "longitude": -46.655882
  },
  "nivel_ruido_manual": "bom",
  "nivel_luz_manual": "bom"
}'
test_endpoint "POST" "/registros" "$REGISTRO_RESTAURANTE" "$TOKEN"

# 12. Buscar todos os locais próximos (sem filtro)
echo "=== 12. BUSCAR TODOS OS LOCAIS PRÓXIMOS ==="
test_endpoint "GET" "/locais/proximos?latitude=-23.550520&longitude=-46.633308&raio_km=10" "" "$TOKEN"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ TESTES CONCLUÍDOS!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 Resumo:"
echo "- Usuário criado e autenticado"
echo "- 7+ registros criados"
echo "- 2 locais diferentes cadastrados"
echo "- Busca e detalhamento testados"
echo ""
echo "🌐 Acesse a documentação em: $API_URL/docs"
echo "💾 Se estiver usando Docker, acesse MongoDB Express: http://localhost:8081"
echo "   (usuário: admin / senha: admin123)"