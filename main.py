import moviepy.video.VideoClip
from pytube import YouTube, extract
from moviepy.editor import VideoFileClip
from time import time
import asyncio
import pyaudio
import wave
import os


async def delayed_function(t, func, asc=False, *args):
    expected = time() + t
    while True:
        if time() < expected:
            continue
        func(*args) if not asc else asyncio.run(func(*args))
        break


def create_folder(folder_path):
    not os.path.exists(folder_path) and os.mkdir(folder_path)


def download(link):
    video_id = extract.video_id(link)
    video_obj = YouTube(link)
    create_folder(f"./cache/{video_id}")
    try:
        filename = f"{video_id}.mp4"
        path = video_obj.streams.filter(res="144p").first().download(f'cache/{video_id}/video', filename)
    except:
        print("Je n'ai pas pu télécharger la vidéo YouTube.")
        exit(403)
    print(f"Le téléchargement a été fait avec succès vers {path}")
    divide(video_id)


def divide(video_id):
    full_video = VideoFileClip(f"./cache/{video_id}/video/{video_id}.mp4")
    create_folder(f"./cache/{video_id}/audio")
    full_video.audio.write_audiofile(f"./cache/{video_id}/audio/{video_id}.wav")
    current_duration = full_video.duration
    single_duration = 60
    i = 1
    create_folder(f"./cache/{video_id}/video_parts")
    while current_duration > single_duration:
        clip = full_video.subclip(current_duration - single_duration, current_duration)
        current_duration -= single_duration
        current_video = os.path.realpath(f"./cache/{video_id}/video_parts/{video_id}_{i}.mp4")
        clip.to_videofile(current_video, codec="libx264",
                          temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')
        i += 1
    else:
        clip = full_video.subclip(0, current_duration)
        current_video = os.path.realpath(f"./cache/{video_id}/video_parts/{video_id}_{i}.mp4")
        clip.to_videofile(current_video, codec="libx264",
                          temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')
    transform(video_id, i)


def transform(video_id, n):
    create_folder(f"./cache/{video_id}/gif_parts")
    for i in range(1, n + 1):
        path = f"./cache/{video_id}/video_parts/{video_id}_{i}.mp4"
        video_part = VideoFileClip(path)
        new_path = f"./cache/{video_id}/gif_parts/{video_id}_{i}.gif"
        video_part.write_gif(new_path, fps=30, program='ffmpeg')
    start(video_id, n)


def start(video_id, n):
    asyncio.run(launch(video_id, 1, n))
    sound(video_id)


def sound(video_id):
    wf = wave.open(f"./cache/{video_id}/audio/{video_id}.wav", 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(1024)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(1024)


async def launch(video_id, i, n):
    global height, width
    path = f"./cache/{video_id}/gif_parts/{video_id}_{i}.gif"
    print(f"Lancement du gif à: {path}")
    os.system(f"sudo ./led-video-viewer {path} --led-rows={height} --led-cols={width}")
    if i < n:
        asyncio.run(delayed_function(60, launch, True, video_id, i + 1, n))


if __name__ == '__main__':
    height = int(input("Quelle est la hauteur en led ? "))
    width = int(input("Quelle est la largeur en led ? "))
    link = input("Entrez un lien YouTube afin de commencer le téléchargement: ")
    download(link)
