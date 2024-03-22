from flask import Flask, render_template, request, send_file
from pydub import AudioSegment
from pyannote.audio import Pipeline
from datetime import datetime
import re
import webvtt
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    # Récupérer le fichier uploadé par l'utilisateur
    uploaded_file = request.files['file']
    uploaded_file.save('download.wav')

    # Effectuer le traitement
    # Ajoutez ici le code pour le traitement audio et la génération de lexica.html

    # Une fois que le traitement est terminé, renvoyer la page HTML générée
    with open('lexicap.html', 'r') as file:
        lexica_html = file.read()
    return lexica_html

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    # Télécharger des fichiers à partir du répertoire
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
