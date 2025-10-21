# 🧪 GUIA DE TESTE COM DADOS REAIS

## ✅ Ambiente Pronto!

Seu aplicativo está rodando **com dados de teste realistas** pré-carregados no banco de dados.

---

## 📊 Dados Disponíveis

| Métrica | Quantidade |
|---------|-----------|
| **Usuários** | 3 usuários de teste |
| **Locais** | 5 locais em São Paulo |
| **Registros** | 7 medições de ruído/luz |

### Usuários de Teste

```
Email: ana@test.com
Senha: 123456

Email: carlos@test.com
Senha: 123456

Email: maria@test.com
Senha: 123456
```

### Locais com Dados

1. **Starbucks Paulista** (Cafeteria)
   - 62.5 dB | 380 Lux
   
2. **Biblioteca Municipal** (Biblioteca)
   - 38.0 dB | 320 Lux
   
3. **Shopping Imigrantes** (Shopping)
   - 72.0 dB | 650 Lux
   
4. **Restaurante Bella Italia** (Restaurante)
   - 68.5 dB | 280 Lux
   
5. **Metrô República** (Transporte Público)
   - 78.0 dB | 200 Lux

---

## 🌐 Acessar a Aplicação

### Frontend (Interface)
👉 **http://localhost:3000**

### API Documentation
👉 **http://localhost:8000/docs** (Swagger UI)

### Health Check
👉 **http://localhost:8000/health**

---

## 🧪 O Que Testar

### 1. **Login e Dashboard**
   - Abra http://localhost:3000
   - Clique em "Login"
   - Use: `ana@test.com` / `123456`
   - Você verá o dashboard com estatísticas dos dados

### 2. **Mapa de Locais**
   - Clique na aba "🔍 Buscar Locais"
   - Você verá um mapa com 5 locais marcados
   - Marcadores coloridos indicam nível de ruído:
     - 🟢 Verde = Bom (< 45 dB)
     - 🟡 Amarelo = Ok (45-55 dB)
     - 🟠 Laranja = Atenção (55-65 dB)
     - 🔴 Vermelho = Ruim (> 65 dB)

### 3. **Buscar por Nome ou Tipo**
   - Use a caixa de busca para filtrar locais
   - Filtre por tipo de ambiente (Cafeteria, Biblioteca, etc.)

### 4. **Registrar Nova Medição Manual**
   - Clique em "📊 Registrar Leitura"
   - Clique em "📍 Obter Localização" (simula GPS)
   - Classifique o ambiente: Bom / Ok / Atenção / Ruim
   - Clique em "✅ Enviar"

### 5. **Medir com Sensores**
   - Clique em "📱 Medir com Sensores"
   - Clique em "🎤 Medir Ruído" (permite acesso ao microfone)
   - Clique em "💡 Medir Luz" (permite acesso à câmera)
   - Veja os resultados em dB e Lux
   - Clique "✅ Salvar Medição"

### 6. **Perfil do Usuário**
   - Clique em "👤 Perfil"
   - Veja informações do usuário logado

---

## 📈 Dados Esperados no Mapa

Ao abrir a aba "Buscar Locais", você deve ver:

```
🗺️ Mapa com 5 marcadores:
  ├─ 🟡 Starbucks (62.5dB - Ok)
  ├─ 🟢 Biblioteca (38dB - Bom)
  ├─ 🔴 Shopping (72dB - Ruim)
  ├─ 🔴 Restaurante (68.5dB - Ruim)
  └─ 🔴 Metrô (78dB - Ruim)
```

---

## 🔧 Scripts Úteis

### Popular mais dados
```bash
cd /Users/kimgomes/Desktop/sensorial_app
python3 criar_dados_teste.py
```

### Reiniciar com dados carregados
```bash
cd /Users/kimgomes/Desktop/sensorial_app/estrutura-back
python3 run_with_test_data.py
```

### Ver API Documentation
Abra: http://localhost:8000/docs

---

## 🐛 Troubleshooting

### "Frontend não carrega"
```bash
# Reiniciar frontend
killall python3
cd /Users/kimgomes/Desktop/sensorial_app
python3 serve_frontend.py
```

### "API retorna erro"
```bash
# Verificar status
curl http://localhost:8000/health

# Reiniciar backend com dados
cd /Users/kimgomes/Desktop/sensorial_app/estrutura-back
python3 run_with_test_data.py
```

### "Sensores não funcionam"
- Use navegador Chrome, Firefox ou Safari
- Permita acesso ao microfone e câmera
- Teste em https ou localhost

---

## 📝 Notas Importantes

✅ **Dados em Memória**: Os dados são salvos em memória RAM. Ao reiniciar o servidor, eles serão perdidos.

✅ **Classificação Automática**: Os valores de dB e Lux são classificados automaticamente segundo as normas ABNT.

✅ **Geolocalização Simulada**: O botão "📍 Obter Localização" simula GPS (não requer GPS real).

✅ **Múltiplos Usuários**: Você pode fazer logout e testar com outros usuários (carlos@test.com ou maria@test.com).

---

## 🎯 Fluxo Recomendado de Teste

1. **Acesse o frontend** → http://localhost:3000
2. **Faça login** → ana@test.com / 123456
3. **Explore o Dashboard** → Veja estatísticas
4. **Vá para Mapa** → Veja os 5 locais com dados
5. **Teste Busca** → Filtre por nome ou tipo
6. **Registre Manual** → Clique em "Registrar Leitura"
7. **Teste Sensores** → Clique em "Medir com Sensores"
8. **Veja Documentação** → http://localhost:8000/docs

---

## 📚 Documentação Complementar

- `ARQUITETURA.md` - Visão geral da arquitetura
- `GUIA_USO.md` - Guia completo de uso
- `SENSORES_TECNICO.md` - Como os sensores funcionam
- `FLUXO_MEDICOES.md` - Fluxo de medições
- `MELHORIAS.md` - Melhorias implementadas

---

**Bom teste! 🚀** Se tiver dúvidas, verifique a documentação ou os endpoints em `/docs`.
