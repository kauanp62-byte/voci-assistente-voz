from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # ✅ Nome correto

def perguntar_ia(mensagem_usuario):
    print("A IA está pensando...")
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages = [
            {"role": "system", "content": "Você é um assistente de voz prestativo. Responda de forma concisa e natural."},
            {"role": "user", "content": mensagem_usuario}
        ],
    )
    return completion.choices[0].message.content

# Teste no final do arquivo
if __name__ == "__main__":
    resposta = perguntar_ia("Olá, você está funcionando?")
    print(f"Resposta: {resposta}")

