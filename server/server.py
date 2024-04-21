from subprocess import Popen, PIPE
from threading import Thread
from flask import Flask, Response
import pyaudio
import json

FORMAT = pyaudio.paFloat32
CHANNELS = 1
CHUNK_SIZE = 1024
SAMPLE_RATE = 16000

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello World!"


def read_audio(inp, audio):
    while True:
        inp.write(audio.read(num_frames=CHUNK_SIZE))

def read_config():
    with open('config/config.json') as f:
        config = json.load(f)
    return config

def response():
    a = pyaudio.PyAudio().open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=config['device_id'],
        frames_per_buffer=CHUNK_SIZE
    )

    c = f'ffmpeg -re -f f32le -acodec pcm_f32le -ar {SAMPLE_RATE} -ac {CHANNELS} -i pipe: -f mp3 pipe:'
    p = Popen(c.split(), stdin=PIPE, stdout=PIPE)
    Thread(target=read_audio, args=(p.stdin, a), daemon=True).start()

    while True:
        yield p.stdout.readline()


@app.route('/audio_feed', methods=['GET'])
def audio_feed():
    return Response(
        response(),
        headers={
            # NOTE: Ensure stream is not cached.
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
        },
        mimetype='audio/mpeg')


if __name__ == "__main__":
    config = read_config()
    app.run(host='0.0.0.0')