import edge_tts
import asyncio
from playsound import playsound
import os

async def gerar_e_tocar(texto):
    VOICE = "pt-BR-AntonioNeural"
    OUTPUT_FILE = "resposta_ia.mp3"

    print("Gerando resposta em áudio...")

    try:
        tts = edge_tts.communicate(texto, VOICE)
        await tts.save(OUTPUT_FILE)

        playsound(OUTPUT_FILE)

        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)

    except Exception as e:
        print("Erro no speaker:", e)

if __name__ == "__main__":
    teste_texto = "Olá! Esta é uma resposta de teste do assistente de voz."
    asyncio.run(gerar_e_tocar(teste_texto))