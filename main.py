from utils import create_folder, download, start
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
    width = result.get('width', None)
    height = result.get('height', None)
    media = result.get('media', None)
    link = result.get('link', None)
    source = result.get('source', None)
    if not width or not height:
        pass
        return error('Erreur lors du lancement du script:\nLe paramètre width/height est manquant.')
    elif not media or not link:
        return error('Erreur lors du lancement du script:\nLa méthode ou le lien est manquant.')
    if media in ('image', 'gif'):
        path = os.path.realpath(link)
        image = path.endswith('.gif')
        start(path=path, isImage=image)
    elif media == 'video':
        if source == 'path':
            path = os.path.realpath(link)
            start(path=path, isImage=False)
        elif source == 'internet':
            path = download(os.path.realpath(link))
            if type(path) is not str:
                return error("Erreur lors du téléchargement de la vidéo YouTube:\n" + path[1])
            start(path=path, isImage=False)

    return render_template('submit.html', media=media, source=source, link=link)


app.run(debug=True)

if False and __name__ == '__main__':
    create_folder("./cache")
    options = RGBMatrixOptions()
    options.rows = height
    options.cols = width
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'regular'