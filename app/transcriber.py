from faster_whisper import WhisperModel
import os

model_size = "base"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

def transcrever_audio(file_path):
    print("Transcrevendo áudio...")
    segments, info = model.transcribe(file_path, beam_size=5, language="pt")

    texto = ""
    for segment in segments:
        texto += segment.text
        
    return texto.strip()

if __name__ == "__main__":
    if os.path.exists("teste.wav"):
        resultado = transcrever_audio("teste.wav")
        print(f"Resultado do teste: {resultado}")

    
