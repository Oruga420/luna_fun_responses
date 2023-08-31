import gradio as gr
import openai, config, subprocess
import os
from gtts import gTTS
from pydub import AudioSegment
import pygame
import tempfile
import requests
from bs4 import BeautifulSoup
from newspaper import Article

ffmpeg_bin_path = r'C:\Users\chuck\OneDrive\Desktop\Dev\ffmpeg\bin'
if ffmpeg_bin_path not in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + ffmpeg_bin_path

openai.api_key = ""

messages = [{"role": "system", "content": 'You are Luna a stoner assistant better than Jarvis from Ironman but still stoner we live in canada its 2023. keep it short you can talk using whisper API from open AI , your brain is powered by GPT4 and we love conspiracy theories and aliens and all that cool shit and voice provided by google for now and you are the bomb! please help generating crazy conspiracy theories.'}]

def extract_text_from_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    article = Article(url, headers=headers)
    article.download()
    article.parse()
    text = article.text
    return text

def generate_summary(text, length):
    input_message = {
        "role": "user",
        "content": f"Yo yo, generate a conspiracy theory like you're talking to a 50-year-old stoner. Make it {length} words: {text}"
    }

    intro_message = {
        "role": "system",
        "content": "You are a generate a conspiracy theory. Generate a Conspiracy theory of the given text."
    }

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[intro_message, input_message]
    )
    
    summary = response['choices'][0]['message']['content'].strip()
    messages.append(input_message)
    messages.append({"role": "assistant", "content": summary})

    return summary

def transcribe(audio, url_text):
    global messages

    if audio:
        recorded_audio = AudioSegment.from_file(audio)
        converted_audio = 'converted_audio.wav'
        recorded_audio.export(converted_audio, format='wav')

        with open(converted_audio, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        
        messages.append({"role": "user", "content": transcript["text"]})
        url = transcript["text"].replace("summarize url", "").strip()
    else:
        url = url_text.strip()

    text = extract_text_from_url(url)
    summary = generate_summary(text, 50)

    tts = gTTS(summary, lang='en', slow=False)
    tts.save('temp_response.wav')

    response_audio = AudioSegment.from_file('temp_response.wav', format='mp3')
    temp_file_descriptor, temp_file_path = tempfile.mkstemp()
    response_audio.export(temp_file_path, format='wav')
    os.close(temp_file_descriptor)
    
    pygame.mixer.init()
    pygame.mixer.music.load(temp_file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    os.remove(temp_file_path)

    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    return chat_transcript

ui = gr.Interface(
    fn=transcribe,
    inputs=[gr.Audio(source="microphone", type="filepath"), "text"],
    outputs="text",
    title="Lunas Summary Lab"
).launch(share=True)
ui.launch(share=True)