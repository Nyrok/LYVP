from pytube import YouTube, extract
from PIL import Image
from moviepy.editor import VideoFileClip
from os import mkdir, path
from time import time, sleep
from rgbmatrix import RGBMatrix


async def delayed_function(t, func, asc=False, *args):
    expected = time() + t
    while True:
        if time() < expected:
            continue
        func(*args) if not asc else await func(*args)
        break


def create_folder(folder_path):
    not path.exists(folder_path) and mkdir(folder_path)


def download(link, width, height):
    video_id = extract.video_id(link)
    video_obj = YouTube(link, on_progress_callback=__on_progress)
    video_obj.register_on_progress_callback(__on_progress)
    create_folder(f"./cache/youtube/{video_id}")
    filename = f"{video_id}.mp4"
    try:
        path = video_obj.streams.filter(res="144p").first().download(f'cache/youtube/{video_id}/video', filename)
    except Exception as e:
        print("Je n'ai pas pu télécharger la vidéo YouTube.\nErreur: " + str(e))
        return None, str(e)
    print(f"Le téléchargement a été fait avec succès vers {path}")
    full_video = VideoFileClip(f"./cache/youtube/{video_id}/video/{video_id}.mp4")
    full_video = full_video.resize((width, height))
    new_path = f"./cache/youtube/{video_id}/gif/{video_id}.gif"
    full_video.write_gif(new_path, fps=30, program='ffmpeg')
    return new_path

def start(options, path, isImage=False, loop=True):
    matrix = RGBMatrix(options=options)
    if not isImage:
        print(f"Lancement du gif à: {path}")
        gif = Image.open(path.realpath(path))
        num_frames = gif.n_frames
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
            if loop:
                start(options, path, isImage, loop)
    else:
        print(f"Lancement de l'image à: {path}")
        image = Image.open(path.realpath(path))
        image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
        matrix.SetImage(image.convert('RGB'))
        while loop:
            sleep(100)

def __on_progress(vid, chunk, bytes_remaining):
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


def __percent(t, total):
    return (float(t) / float(total)) * float(100)
