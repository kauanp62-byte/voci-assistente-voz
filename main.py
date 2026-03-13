import asyncio
from app.recorder import gravar_audio
from app.transcriber import transcrever_audio
from app.brain import perguntar_ia
from app.speaker import gerar_e_tocar

async def fluxo_principal():
    print("Iniciando o assistente de voz...")

    #1. Grava 5 segundos do microfone
    arquivo_audio = gravar_audio(duracao=5)

    #2. transcreve o áudio para texto localmente
    texto_usuario = transcrever_audio(arquivo_audio)

    if not texto_usuario:
        print("Nenhum áudio capturado. Tente novamente.")
        return
    
    print(f"Você disse: {texto_usuario}")

    #3. Envia o texto para a IA e recebe a resposta
    resposta_ia = perguntar_ia(texto_usuario)
    print("Resposta da IA à sua pergunta: " + resposta_ia)

    #4 converte a resposta em voz e toca
    await gerar_e_tocar(resposta_ia)

    print("Processo concluído. Você pode fazer outra pergunta ou encerrar o programa.")

if __name__ == "__main__":
    #roda um loop assincrono
    try:
        asyncio.run(fluxo_principal())
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")