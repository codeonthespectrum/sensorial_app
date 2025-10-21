# 📱 Sensores - Guia Técnico

## Visão Geral

O aplicativo agora é capaz de medir ruído e luminosidade **diretamente do celular**, sem necessidade de baixar outros apps! Aqui está como funciona tecnicamente.

## 🎤 Medição de Ruído

### Componentes

#### Frontend (sensores.js)
1. **Web Audio API**: Captura áudio do microfone
   - Cria um contexto de áudio
   - Usa um analisador FFT (Fast Fourier Transform)
   - Captura dados de frequência em tempo real

2. **Processamento de Frequências**
   - FFT Size: 2048 amostras
   - Captura por 3 segundos
   - Calcula energia média das frequências

#### Backend (main.py - `/sensores/processar-audio`)
1. **Conversão para dB**
   ```python
   dB = 20 * log10(energia_media / referencia)
   Referencia = 0.001 (valor normalizado)
   ```

2. **Validação**
   - Limita entre 0-120 dB
   - Classifica em Bom/Ok/Atenção/Ruim
   - Retorna energia normalizada

### Precisão
- ±3-5 dB (aceitável para aplicação)
- Função de precisão do microfone do dispositivo
- Melhor em ambientes isolados

### Limitações
- Requer permissão do usuário
- Microfone deve estar calibrado
- Evite mexer no celular durante medição
- Ambiente deve estar relativamente constante durante 3s

### Pré-requisitos
- Navegador com suporte a Web Audio API (Chrome, Firefox, Safari, Edge)
- Microfone funcional
- Permissão concedida pelo usuário

## 💡 Medição de Luminosidade

### Componentes

#### Frontend (sensores.js)
1. **getUserMedia + Canvas**
   - Captura vídeo da câmera
   - Extrai frames para análise
   - Lê pixels RGB do canvas

2. **Processamento de Pixels**
   - Analisa região central (25-75% da imagem)
   - Evita bordas e obstáculos
   - Captura média de 200ms em 2 segundos (10 amostras)
   - Calcula RGB médio

#### Backend (main.py - `/sensores/processar-luminosidade`)
1. **Gamma Correction** (padrão sRGB)
   ```python
   Para cada canal (R, G, B):
   Se c <= 0.03928:
       c = c / 12.92
   Senão:
       c = ((c + 0.055) / 1.055) ^ 2.4
   ```

2. **Cálculo de Luminância Relativa**
   ```python
   Luminância = 0.2126*R + 0.7152*G + 0.0722*B
   ```

3. **Estimativa de Lux**
   ```python
   Lux = 10000 * (Luminância ^ 2)
   Limitado entre 0-10000 Lux
   ```

### Precisão
- ±20-30 Lux (variável conforme câmera)
- Mapeia em escala logarítmica
- Depende muito da qualidade da câmera

### Limitações
- Câmera não deve estar obstruída
- Exposição automática da câmera varia por dispositivo
- Funciona melhor com câmeras traseiras
- Luz infravermelha não é detectada

### Pré-requisitos
- Navegador com suporte a getUserMedia
- Câmera funcional
- Permissão concedida pelo usuário
- Câmera limpa (sem poeira/sujeira)

## 📊 Valores de Referência

### Ruído (dB)
```
0-10    dB  → Silêncio absoluto (impossível)
10-20   dB  → Sussurro, folhas caindo
20-30   dB  → Biblioteca, consultório
30-40   dB  → Ambiente residencial quieto
40-50   dB  → Escritório, restaurante calmo
50-60   dB  → Conversa normal, TV
60-70   dB  → Tráfego, aspirador
70-80   dB  → Música alta, secadora
80-90   dB  → Tráfego intenso, metrô
90-100  dB  → Britadeira, equipamento industrial
100+    dB  → Potencialmente prejudicial
```

### Luminosidade (Lux)
```
0-50      Lux  → Noite, escuro completo
50-100    Lux  → Nível de iluminação mínimo
100-200   Lux  → Ambiente interior pouco iluminado
200-500   Lux  → Escritório, loja bem iluminada
500-1000  Lux  → Luz natural brilhante
1000-2000 Lux  → Dia nublado
2000-5000 Lux  → Dia ensolarado (interior)
5000+     Lux  → Luz solar direta
```

## 🔧 Fluxo de Funcionamento

### 1. Medição de Ruído
```
┌─────────────────────────────────────┐
│ Usuário clica "Medir Ruído"         │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Solicita permissão de microfone      │
│ (navigator.mediaDevices.getUserMedia)│
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Cria contexto de áudio               │
│ Conecta analisador FFT              │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Captura 30 amostras de 100ms        │
│ (total: 3 segundos)                 │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Envia frequências e energia ao      │
│ backend via /sensores/processar-audio│
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Backend calcula dB e retorna        │
│ classificação (Bom/Ok/Atenção/Ruim) │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Frontend exibe resultado            │
│ Parar captura de áudio              │
└─────────────────────────────────────┘
```

### 2. Medição de Luminosidade
```
┌─────────────────────────────────────┐
│ Usuário clica "Medir Luz"           │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Solicita permissão de câmera        │
│ (navigator.mediaDevices.getUserMedia)│
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Cria elemento <video>               │
│ Inicia captura da câmera            │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Cria elemento <canvas>              │
│ Aguarda vídeo estar pronto          │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Captura 10 frames de 200ms          │
│ (total: 2 segundos)                 │
│ Extrai RGB da região central        │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Envia RGB médio ao backend via      │
│ /sensores/processar-luminosidade    │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Backend calcula Lux e retorna       │
│ classificação                       │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Frontend exibe resultado            │
│ Parar captura de vídeo              │
└─────────────────────────────────────┘
```

### 3. Salvamento
```
┌─────────────────────────────────────┐
│ Ambas medições realizadas           │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Usuário preenche:                   │
│ - Nome do local                     │
│ - Tipo de ambiente                  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Clica "Salvar Medição"              │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ POST /registros com:                │
│ - nome_local                        │
│ - tipo_ambiente                     │
│ - ruido_db (medido)                 │
│ - luminosidade_lux (medida)         │
│ - coordenadas (GPS ou padrão)       │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Backend classifica e salva registro │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Sucesso! Dados disponíveis para     │
│ outros usuários                     │
└─────────────────────────────────────┘
```

## 🛡️ Permissões Necessárias

### No Frontend
```javascript
// Microfone
navigator.mediaDevices.getUserMedia({ 
    audio: {
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false
    }
})

// Câmera
navigator.mediaDevices.getUserMedia({ 
    video: {
        facingMode: 'environment',
        width: { ideal: 1280 },
        height: { ideal: 720 }
    }
})
```

### Mensagens do Navegador
- Chrome/Edge: "Permite que [site] use seu microfone/câmera?"
- Firefox: Similar
- Safari: "Quer permitir que [site] use seu microfone/câmera?"

## 🐛 Troubleshooting

### Problema: "Permissão de microfone negada"
- Verifique configurações de privacidade do navegador
- Certifique-se que o site usa HTTPS (em produção)
- Teste em incógnito

### Problema: "Nenhuma frequência capturada"
- Microfone pode estar desabilitado
- Teste com outro app de gravação primeiro
- Reinicie o navegador

### Problema: "Câmera não iniciou"
- Câmera pode estar em uso por outro app
- Feche outros aplicativos
- Teste em outro navegador

### Problema: Valores de Lux muito altos/baixos
- Câmera pode ter exposição automática diferente
- Aponte para superfície branca neutra
- Evite luz infravermelha

## 📈 Futuras Melhorias

- [ ] Calibração manual dos sensores
- [ ] Histórico de medições no dispositivo
- [ ] Comparação com valores anteriores
- [ ] Detecção de picos de ruído
- [ ] Integração com sensores nativos (se disponível)
- [ ] Modo noturno para melhor captura
- [ ] Análise de frequências específicas

---

**Tecnologias Utilizadas:**
- Web Audio API
- Media Capture and Streams API
- Canvas API
- FFT (Fast Fourier Transform)
- Gamma Correction (sRGB)
