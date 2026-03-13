import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

def gravar_audio(nome_arquivo="temp_audio.wav", duracao = 5):
    fs = 44100
    print(f"Gravando áudio por {duracao} segundos...")

    gravacao = sd.rec(int(duracao * fs), samplerate=fs, channels=1)
    sd.wait()

    write(nome_arquivo, fs, gravacao)
    print("Gravação concluída e salva como " + nome_arquivo)
    return nome_arquivo