from utils import create_folder, download, start, convert
from rgbmatrix import RGBMatrixOptions
import os
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('form.html')


@app.route('/submit', methods=['POST'])
def submit():
    error = lambda str: render_template('error.html', error=str)
    result = request.form
    media = result.get('media', None)
    link = result.get('link', None)
    source = result.get('source', None)
    loop = result.get('loop', True)
    if not media or not link:
        return error('Erreur lors du lancement du script:\nLa méthode ou le lien est manquant.')
    width = 192
    height = 128
    options = RGBMatrixOptions()
    options.rows = 64
    options.cols = 64
    options.chain_length = 3 
    options.parallel = 2
    options.hardware_mapping = 'regular'
    if media in ('image', 'gif'):
        p = os.path.realpath(link)
        image = not p.endswith('.gif')
        start(options=options, p=p, isImage=image, loop=loop)
    elif media == 'video':
        if source == 'path':
            path = os.path.realpath(link)
            new_path = convert(path, width, height)
            start(options=options, p=new_path, isImage=False, loop=loop)
        elif source == 'internet':
            path = download(os.path.realpath(link), width=width, height=height)
            if type(path) is not str:
                return error("Erreur lors du téléchargement de la vidéo YouTube:\n" + path[1])
            start(options=options, p=path, isImage=False, loop=loop)

    return render_template('submit.html', media=media, source=source, link=link)

if __name__ == '__main__':
    create_folder("./cache")
    create_folder("./cache/youtube")
    app.run(debug=True, port=8080)
