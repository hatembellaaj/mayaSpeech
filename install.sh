pip install -U yt-dlp
pip install pydub
pip install   pyannote.audio
pip install numpy --pre torch torchvision torchaudio --force-reinstall --index-url
wget -O - -q  https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz | xz -qdc| tar -x
pip install git+https://github.com/openai/whisper.git
whisper dz.wav --language fr --model large
pip install -U webvtt-py
