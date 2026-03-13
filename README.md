# 🎙️ Voci — Assistente de Voz com IA

Um assistente de voz local em Python que grava sua voz, transcreve o áudio, consulta uma IA e exibe a resposta em texto — tudo em português.

---

## 🖥️ Demonstração

```
Você fala  →  Whisper transcreve  →  Groq (Llama 3.3) responde  →  Texto exibido na tela
```

---

## ✨ Funcionalidades

- 🎤 Gravação de áudio pelo microfone
- 📝 Transcrição local com **Faster-Whisper**
- 🧠 Respostas inteligentes via **Groq API** (Llama 3.3 70B)
- 🖼️ Interface gráfica minimalista com **Tkinter**

---

## 📁 Estrutura do Projeto

```
Voice Assistant/
├── .env                  # Variáveis de ambiente (não versionar!)
├── main.py               # Fluxo principal via terminal
├── ui.py                 # Interface gráfica (Tkinter)
└── app/
    ├── brain.py          # Integração com a IA (Groq)
    ├── recorder.py       # Gravação de áudio
    ├── speaker.py        # Síntese de voz (Edge-TTS)
    └── transcriber.py    # Transcrição de áudio (Faster-Whisper)
```

---

## ⚙️ Requisitos

- Python 3.10+
- Windows 10/11
- Microfone
- [FFmpeg](https://ffmpeg.org/download.html) instalado e no PATH
- Conta gratuita na [Groq](https://console.groq.com)

---

## 🚀 Instalação

**1. Clone o repositório**
```bash
git clone https://github.com/kauanp62-byte/voci-assistente-voz.git
cd voci-assistente-voz
```

**2. Crie e ative o ambiente virtual**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**3. Instale as dependências**
```bash
pip install groq python-dotenv sounddevice scipy numpy faster-whisper edge-tts playsound==1.2.2
```

**4. Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:
```
GROQ_API_KEY=sua_chave_aqui
```

> Obtenha sua chave gratuita em [console.groq.com](https://console.groq.com)

---

## ▶️ Como Usar

**Interface gráfica (recomendado):**
```bash
python ui.py
```

**Via terminal:**
```bash
python main.py
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Função | Custo |
|---|---|---|
| [Groq API](https://groq.com) | IA (Llama 3.3 70B) | Gratuito |
| [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) | Transcrição de voz | Gratuito |
| [Edge-TTS](https://github.com/rany2/edge-tts) | Síntese de voz | Gratuito |
| [SoundDevice](https://python-sounddevice.readthedocs.io) | Gravação de áudio | Gratuito |
| Tkinter | Interface gráfica | Nativo Python |

---

## 📝 Observações

- O modelo Whisper `base` é baixado automaticamente na primeira execução (~145 MB)
- O limite gratuito da Groq é de ~14.400 requisições/dia
- O arquivo `.env` **nunca** deve ser versionado no Git

---

## 📄 Licença

MIT License — sinta-se livre para usar, modificar e distribuir.