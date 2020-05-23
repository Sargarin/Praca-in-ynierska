import pyaudio
import wave
import io
import os
from datetime import datetime
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from projekt.tts import synthesize_text_with_audio_profile

#Metoda odpoweidzialna za odsłuchanie wypowiedzi użytkownika wraz z zapisem do pliku .wav
def listen_for_speech(time: int):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    seconds = time
    filename = "output.wav"
    p = pyaudio.PyAudio()
    print('Recording')
    stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
    frames = []
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    print('Finished recording')
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

#funkcja pomocnicza przeprowadzająca zapis otrzymanego dzwięku do tymczasowego pliku
def save_speech(data, p):
    filename = 'output_' + str(int(datetime.time()))
    data = ''.join(data)
    wf = wave.open(filename + '.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(data)
    wf.close()
    return filename + '.wav'

#Metoda odpoweidzialna za obsługe zapisanej wypowiedzi użytkownika oraz przetworzenie jej na tekst
def stt_google_wav(audio_fname):
    print("Sending ", audio_fname)
    filename = audio_fname
    client = speech.SpeechClient()
    file_name = 'output.wav'
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='pl-pl')
    response = client.recognize(config, audio)
    if len(response.results) == 0:
        synthesize_text_with_audio_profile('Przepraszam, nic nie słyszę.')
    for result in response.results:
        if result == "":
            synthesize_text_with_audio_profile('Przepraszam, nic nie słyszę.')
            break
        print('Transcript: {}'.format(result.alternatives[0].transcript))
        if result.alternatives[0].confidence < 0.75:
            synthesize_text_with_audio_profile('nie zrozumiałam')
            break;
        else:
            return result.alternatives[0].transcript
    os.remove(filename)
    return ""
