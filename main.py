from pytube import YouTube, extract
from moviepy.editor import VideoFileClip
from time import time, sleep
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import asyncio
import pyaudio
import wave
import os


async def delayed_function(t, func, asc=False, *args):
    expected = time() + t
    while True:
        if time() < expected:
            continue
        func(*args) if not asc else await func(*args)
        break


def create_folder(folder_path):
    not os.path.exists(folder_path) and os.mkdir(folder_path)


def on_progress(vid, chunk, bytes_remaining):
    total_size = vid.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    totalsz = (total_size / 1024) / 1024
    totalsz = round(totalsz, 1)
    remain = (bytes_remaining / 1024) / 1024
    remain = round(remain, 1)
    dwnd = (bytes_downloaded / 1024) / 1024
    dwnd = round(dwnd, 1)
    percentage_of_completion = round(percentage_of_completion, 2)

    print(
        f'Download Progress: {percentage_of_completion}%, Total Size:{totalsz} MB, Downloaded: {dwnd} MB, Remaining:{remain} MB')


def percent(t, total):
    return (float(t) / float(total)) * float(100)


def download(link):
    video_id = extract.video_id(link)
    video_obj = YouTube(link, on_progress_callback=on_progress)
    video_obj.register_on_progress_callback(on_progress)
    create_folder(f"./cache/{video_id}")
    filename = f"{video_id}.mp4"
    try:
        path = video_obj.streams.filter(res="144p").first().download(f'cache/{video_id}/video', filename)
    except Exception as e:
        print("Je n'ai pas pu télécharger la vidéo YouTube.\nErreur: " + str(e))
        exit(403)
    print(f"Le téléchargement a été fait avec succès vers {path}")
    create_folder(f"./cache/{video_id}/gif")
    full_video = VideoFileClip(f"./cache/{video_id}/video/{video_id}.mp4")
    new_path = f"./cache/{video_id}/gif/{video_id}.gif"
    full_video.write_gif(new_path, fps=30, program='ffmpeg')
    #divide(video_id)
    start(video_id)


def divide(video_id):
    global width, height
    full_video = VideoFileClip(f"./cache/{video_id}/video/{video_id}.mp4")
    create_folder(f"./cache/{video_id}/audio")
    full_video.audio.write_audiofile(f"./cache/{video_id}/audio/{video_id}.wav")
    current_duration = full_video.duration
    single_duration = 60
    i = 1
    create_folder(f"./cache/{video_id}/video_parts")
    if current_duration > 60:
        while current_duration > single_duration:
            clip = full_video.subclip(current_duration - single_duration, current_duration)
            clip = clip.resize((width, height))
            current_duration -= single_duration
            current_video = os.path.realpath(f"./cache/{video_id}/video_parts/{video_id}_{i}.mp4")
            clip.to_videofile(current_video, codec="libx264",
                              temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')
            i += 1
        else:
            clip = full_video.subclip(0, current_duration)
            clip = clip.resize((width, height))
            current_video = os.path.realpath(f"./cache/{video_id}/video_parts/{video_id}_{i}.mp4")
            clip.to_videofile(current_video, codec="libx264",
                              temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')
    else:
        clip = full_video.subclip(0, current_duration)
        clip = clip.resize((width, height))
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


def start(video_id):
    asyncio.run(sound(video_id))
    launch(video_id)


async def sound(video_id):
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


def launch(video_id):
    global options
    path = f"./cache/{video_id}/gif/{video_id}.gif"
    print(f"Lancement du gif à: {path}")
    gif = Image.open(os.path.realpath(path))
    num_frames = gif.n_frames
    matrix = RGBMatrix(options=options)
    for frame_index in range(0, num_frames):
        gif.seek(frame_index)
        duration = gif.info.get("duration")
        framerate = 0.001 + (duration / 1000 / 2)
        frame = gif.copy()
        frame.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
        canvas = matrix.CreateFrameCanvas()
        canvas.SetImage(frame.convert("RGB"))
        matrix.SwapOnVSync(canvas, framerate_fraction=framerate)
        sleep(framerate)
    else:
        print("L'exécution de la vidéo est terminé")


if __name__ == '__main__':
    create_folder("./cache")
    width = int(input("Quelle est la largeur en led ? "))
    height = int(input("Quelle est la hauteur en led ? "))
    options = RGBMatrixOptions()
    options.rows = height
    options.cols = width
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'regular'
    link = input("Entrez un lien YouTube afin de commencer le téléchargement: ")
    download(link)
