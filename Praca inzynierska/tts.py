#funkcja odpowiedzialna za konwersje tekstu na dzwięk oraz wywołanie otrzymanej treści w odtwarzaczu
def synthesize_text_with_audio_profile(text, effects_profile_id='handset-class-device'):
    from google.cloud import texttospeech
    import pyaudio
    import wave
    chunk = 1024
    p = pyaudio.PyAudio()
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.types.SynthesisInput(ssml=text)
    voice = texttospeech.types.VoiceSelectionParams(language_code='pl-pl', ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)
    audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16, effects_profile_id=[effects_profile_id])
    response = client.synthesize_speech(input_text, voice, audio_config)
    with open('output.wav', 'wb') as out:
        out.write(response.audio_content)
    wf = wave.open('output.wav', 'rb')
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
    data = wf.readframes(chunk)
    while data != b'':
        stream.write(data)
        data = wf.readframes(chunk)
    stream.close()
    p.terminate()
    wf.close()
    return

