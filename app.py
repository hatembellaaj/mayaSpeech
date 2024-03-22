from flask import Flask, render_template, request, send_file
from pydub import AudioSegment
from pyannote.audio import Pipeline
from datetime import datetime
import re
import webvtt
import subprocess
import os
import numpy as np

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

    t1 = 0 * 1000 # works in milliseconds
    t2 = 1 * 60 * 1000

    newAudio = AudioSegment.from_wav("download.wav")

    a = newAudio[t1:t2]
    a.export("audio.wav", format="wav")

    # instantiate the pipeline

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.0",
        use_auth_token="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")

    # run the pipeline on an audio file
    dz = pipeline("audio.wav")

    # dump the diarization output to disk using RTTM format
    with open("diarization.txt", "w") as text_file:
        text_file.write(str(dz))

    print(*list(dz.itertracks(yield_label = True))[:10], sep="\n")

    def millisec(timeStr):
        spl = timeStr.split(":")
        s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
        return s


    dz = open('diarization.txt').read().splitlines()
    dzList = []
    for l in dz:
        start, end =  tuple(re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=l))
        start = millisec(start) #- spacermilli
        end = millisec(end)  #- spacermilli
        lex = not re.findall('SPEAKER_01', string=l)
        dzList.append([start, end, lex])

    print(*dzList[:10], sep='\n')

    audio = AudioSegment.from_wav("download.wav")
    spacermilli = 0
    spacer = AudioSegment.silent(duration=spacermilli)
    audio = spacer.append(audio, crossfade=0)

    audio.export('audio.wav', format='wav')



    sounds = spacer
    segments = []

    dz = open('diarization.txt').read().splitlines()
    for l in dz:
        start, end =  tuple(re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=l))
        start = int(millisec(start)) #milliseconds
        end = int(millisec(end))  #milliseconds

        segments.append(len(sounds))
        sounds = sounds.append(audio[start:end], crossfade=0)
        sounds = sounds.append(spacer, crossfade=0)

    sounds.export("dz.wav", format="wav") #Exports to a wav file in the current path.

    #################################################
    ###### Execute whisper command !

    strWhisper = 'whisper audio.wav  --language fr --model tiny' 
    now = datetime.now()
    print("Current time:", now)
    print("strWhisper : ",strWhisper)
    subprocess.Popen(strWhisper, shell=True, stdout=subprocess.PIPE).stdout.read()


    ######
    captions = [[(int)(millisec(caption.start)), (int)(millisec(caption.end)),  caption.text] for caption in webvtt.read('dz.vtt')]
    print(*captions[:8], sep='\n')

    # we need this fore our HTML file (basicly just some styling)
    preS = '<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <meta http-equiv="X-UA-Compatible" content="ie=edge">\n    <title>Lexicap</title>\n    <style>\n        body {\n            font-family: sans-serif;\n            font-size: 18px;\n            color: #111;\n            padding: 0 0 1em 0;\n        }\n        .l {\n          color: #050;\n        }\n        .s {\n            display: inline-block;\n        }\n        .e {\n            display: inline-block;\n        }\n        .t {\n            display: inline-block;\n        }\n        #player {\n\t\tposition: sticky;\n\t\ttop: 20px;\n\t\tfloat: right;\n\t}\n    </style>\n  </head>\n  <body>\n    <h2>MAYA TEST : whisper-transcription-and-speaker-identification </h2>\n  <div  id="player"></div>\n    <br>\n'
    postS = '\t</body>\n</html>'

    from datetime import timedelta

    html = list(preS)
    spacermilli = 348
    for i in range(len(segments)):
        idx = 0
        for idx in range(len(captions)):
            if captions[idx][0] >= (segments[i] - spacermilli):
                break;

        while (idx < (len(captions))) and ((i == len(segments) - 1) or (captions[idx][1] < segments[i+1])):
            c = captions[idx]

            start = dzList[i][0] + (c[0] -segments[i])

            if start < 0:
                start = 0
            idx += 1

            start = start / 1000.0
            startStr = '{0:02d}:{1:02d}:{2:02.2f}'.format((int)(start // 3600),
                                                    (int)(start % 3600 // 60),
                                                    start % 60)

            html.append('\t\t\t<div class="c">\n')
            html.append(f'\t\t\t\t<a class="l" href="#{startStr}" id="{startStr}">link</a> |\n')
            html.append(f'\t\t\t\t<div class="s"><a href="javascript:void(0);" onclick=setCurrentTime({int(start)})>{startStr}</a></div>\n')
            html.append(f'\t\t\t\t<div class="t">{"[User]" if dzList[i][2] else "[Assistant]"} {c[2]}</div>\n')
            html.append('\t\t\t</div>\n\n')

    html.append(postS)
    s = "".join(html)

    with open("lexicap.html", "w") as text_file:
        text_file.write(s)
    print(s)
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
