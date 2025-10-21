/**
 * Módulo de Sensores
 * Captura áudio e vídeo usando Web APIs
 */

class SensorManager {
    constructor() {
        this.audioContext = null;
        this.mediaStream = null;
        this.videoStream = null;
        this.mediaStreamAudioSourceNode = null;
        this.analyser = null;
        this.isRecording = false;
        this.ruindoMedido = null;
        this.luminosidadeMedida = null;
    }

    // ============= INICIALIZAÇÃO =============

    async inicializarAudio() {
        try {
            // Solicitar permissão para usar o microfone
            this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: false,
                    noiseSuppression: false,
                    autoGainControl: false
                }
            });

            // Criar contexto de áudio
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }

            // Criar nó de fonte
            if (!this.mediaStreamAudioSourceNode) {
                this.mediaStreamAudioSourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);
            }

            // Criar analisador
            if (!this.analyser) {
                this.analyser = this.audioContext.createAnalyser();
                this.analyser.fftSize = 2048;
                this.mediaStreamAudioSourceNode.connect(this.analyser);
            }

            return true;
        } catch (error) {
            console.error('Erro ao acessar microfone:', error);
            throw new Error('Permissão de microfone negada ou não disponível');
        }
    }

    async inicializarVideo() {
        try {
            this.videoStream = await navigator.mediaDevices.getUserMedia({ 
                video: {
                    facingMode: 'environment',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });

            return true;
        } catch (error) {
            console.error('Erro ao acessar câmera:', error);
            throw new Error('Permissão de câmera negada ou não disponível');
        }
    }

    // ============= MEDIÇÃO DE RUÍDO =============

    async medirRuido(duracao = 3000) {
        if (!this.audioContext) {
            await this.inicializarAudio();
        }

        return new Promise((resolve, reject) => {
            const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
            const amostras = [];
            const intervaloMedidas = 100; // ms
            const totalMedidas = Math.floor(duracao / intervaloMedidas);
            let medidasCapturadas = 0;

            const intervalo = setInterval(() => {
                // Obter dados de frequência
                this.analyser.getByteFrequencyData(dataArray);

                // Calcular energia média
                let energiaMedia = 0;
                for (let i = 0; i < dataArray.length; i++) {
                    energiaMedia += dataArray[i];
                }
                energiaMedia = energiaMedia / dataArray.length / 255; // Normalizar 0-1

                amostras.push(energiaMedia);
                medidasCapturadas++;

                if (medidasCapturadas >= totalMedidas) {
                    clearInterval(intervalo);

                    // Calcular média de todas as amostras
                    const energiaMediaFinal = amostras.reduce((a, b) => a + b, 0) / amostras.length;

                    // Converter para array de frequências
                    const frequencias = Array.from(dataArray).map(v => v / 255);

                    resolve({
                        frequencias: frequencias,
                        energia_media: energiaMediaFinal,
                        amostras: amostras
                    });
                }
            }, intervaloMedidas);

            // Timeout de segurança
            setTimeout(() => {
                clearInterval(intervalo);
                if (medidasCapturadas > 0) {
                    const energiaMediaFinal = amostras.reduce((a, b) => a + b, 0) / amostras.length;
                    const frequencias = Array.from(dataArray).map(v => v / 255);
                    resolve({
                        frequencias: frequencias,
                        energia_media: energiaMediaFinal,
                        amostras: amostras
                    });
                } else {
                    reject(new Error('Falha ao capturar áudio'));
                }
            }, duracao + 1000);
        });
    }

    // ============= MEDIÇÃO DE LUMINOSIDADE =============

    async medirLuminosidade(duracao = 2000) {
        if (!this.videoStream) {
            await this.inicializarVideo();
        }

        return new Promise((resolve, reject) => {
            try {
                // Criar elemento de vídeo
                const video = document.createElement('video');
                video.srcObject = this.videoStream;
                video.play();

                // Aguardar vídeo começar
                const onCanPlay = () => {
                    video.removeEventListener('canplay', onCanPlay);

                    // Criar canvas
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    const ctx = canvas.getContext('2d');

                    const amostras = [];
                    const intervaloMedidas = 200; // ms
                    const totalMedidas = Math.floor(duracao / intervaloMedidas);
                    let medidasCapturadas = 0;

                    const intervalo = setInterval(() => {
                        // Desenhar frame de vídeo no canvas
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                        // Obter dados de pixel
                        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                        const dados = imageData.data;

                        // Calcular média de RGB
                        let somaR = 0, somaG = 0, somaB = 0;
                        let pixels = 0;

                        // Pegar apenas o centro da imagem (para evitar bordas)
                        const startX = Math.floor(canvas.width * 0.25);
                        const endX = Math.floor(canvas.width * 0.75);
                        const startY = Math.floor(canvas.height * 0.25);
                        const endY = Math.floor(canvas.height * 0.75);

                        for (let y = startY; y < endY; y++) {
                            for (let x = startX; x < endX; x++) {
                                const idx = (y * canvas.width + x) * 4;
                                somaR += dados[idx];
                                somaG += dados[idx + 1];
                                somaB += dados[idx + 2];
                                pixels++;
                            }
                        }

                        const mediaR = Math.round(somaR / pixels);
                        const mediaG = Math.round(somaG / pixels);
                        const mediaB = Math.round(somaB / pixels);

                        amostras.push({ r: mediaR, g: mediaG, b: mediaB });
                        medidasCapturadas++;

                        if (medidasCapturadas >= totalMedidas) {
                            clearInterval(intervalo);
                            video.pause();
                            video.srcObject = null;

                            // Calcular média final
                            const rgbMedio = {
                                r: Math.round(amostras.reduce((acc, v) => acc + v.r, 0) / amostras.length),
                                g: Math.round(amostras.reduce((acc, v) => acc + v.g, 0) / amostras.length),
                                b: Math.round(amostras.reduce((acc, v) => acc + v.b, 0) / amostras.length)
                            };

                            resolve({
                                r: rgbMedio.r,
                                g: rgbMedio.g,
                                b: rgbMedio.b,
                                amostras: amostras
                            });
                        }
                    }, intervaloMedidas);

                    // Timeout de segurança
                    setTimeout(() => {
                        clearInterval(intervalo);
                        video.pause();
                        video.srcObject = null;

                        if (amostras.length > 0) {
                            const rgbMedio = {
                                r: Math.round(amostras.reduce((acc, v) => acc + v.r, 0) / amostras.length),
                                g: Math.round(amostras.reduce((acc, v) => acc + v.g, 0) / amostras.length),
                                b: Math.round(amostras.reduce((acc, v) => acc + v.b, 0) / amostras.length)
                            };
                            resolve({
                                r: rgbMedio.r,
                                g: rgbMedio.g,
                                b: rgbMedio.b,
                                amostras: amostras
                            });
                        } else {
                            reject(new Error('Falha ao capturar vídeo'));
                        }
                    }, duracao + 1000);
                };

                video.addEventListener('canplay', onCanPlay);

                // Timeout se vídeo não iniciar
                setTimeout(() => {
                    if (video.videoWidth === 0) {
                        reject(new Error('Câmera não iniciou corretamente'));
                    }
                }, 5000);

            } catch (error) {
                reject(error);
            }
        });
    }

    // ============= PROCESSAMENTO NO BACKEND =============

    async processarRuido(frequencias, energiaMedia) {
        try {
            const response = await fetch(`${API_URL}/sensores/processar-audio`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    frequencias: frequencias,
                    energia_media: energiaMedia
                })
            });

            if (!response.ok) {
                throw new Error('Erro ao processar ruído');
            }

            const resultado = await response.json();
            this.ruindoMedido = resultado;
            return resultado;
        } catch (error) {
            console.error('Erro ao processar ruído:', error);
            throw error;
        }
    }

    async processarLuminosidade(r, g, b) {
        try {
            const response = await fetch(`${API_URL}/sensores/processar-luminosidade`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ r, g, b })
            });

            if (!response.ok) {
                throw new Error('Erro ao processar luminosidade');
            }

            const resultado = await response.json();
            this.luminosidadeMedida = resultado;
            return resultado;
        } catch (error) {
            console.error('Erro ao processar luminosidade:', error);
            throw error;
        }
    }

    // ============= LIMPEZA =============

    pararAudio() {
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }
    }

    pararVideo() {
        if (this.videoStream) {
            this.videoStream.getTracks().forEach(track => track.stop());
            this.videoStream = null;
        }
    }

    pararTudo() {
        this.pararAudio();
        this.pararVideo();

        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
    }
}

// Instância global
const sensorManager = new SensorManager();
