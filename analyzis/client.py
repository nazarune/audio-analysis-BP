import requests
from multiprocessing import Process
from subprocess import Popen, PIPE
import time
from datetime import datetime
import asyncio
from shazamio import Shazam
import audio_inference
import speech_rec
import json
import paho.mqtt.client as mqtt
import music_inference
import os
import warnings
warnings.filterwarnings('ignore')

def read_config():
    with open('config/config.json') as f:
        config = json.load(f)
    return config

def trscrb_audio(output_file):
    config = read_config()
    temp_file = output_file[:-4] + '.wav'
    cmd2 = [
        "ffmpeg",
        "-i", output_file,  # read from stdin
        temp_file
    ]
    process2 = Popen(cmd2, stdin=PIPE)
    process2.wait()
    text = speech_rec.transcribe(temp_file, config['lang_locale'])
    send_to_mqtt(False, False, text)
    os.remove(temp_file)

def analyze_music(output_file):
    res = {'file': output_file}
    info_track = asyncio.run(find_music(output_file))
    if bool(info_track['matches']) == True:
        res['artist'] = info_track['track']['subtitle']
        res['title'] = info_track['track']['title']
        res['genre'] = info_track['track']['genres']['primary']

    res['tags'] = music_inference.inference(output_file)
    send_to_mqtt(False, True, res)

async def find_music(output_file):
    shazam = Shazam()
    out = await shazam.recognize_song(output_file)
    return out

def send_to_mqtt(isAst, isMusic, res_list):
    config = read_config()
    # convert a list to json format
    json_data = json.dumps(res_list)
    
    client = mqtt.Client()
    client.connect(config['mqtt_server'], config['mqtt_port'])

    if isAst:
        client.publish(config['general_topic'], json_data)
    elif isMusic: 
        client.publish(config['music_topic'], json_data)
    else: 
        client.publish(config['transcribe_topic'], json_data)
    
    client.disconnect()


def analyze_audio(output_file):
    results = audio_inference.inference(output_file)
    send_to_mqtt(True, False, results)
    if 'Music' in results:
        if results.get('Music') >= 0.5:
            analyze_music(output_file)
            return
    if 'Speech' in results:
        if results.get('Speech') >= 0.5:
            trscrb_audio(output_file)
            return
    

def download_hls_stream(url, output_file, duration_sec):
    # download the HLS stream
    response = requests.get(url, stream=True)
    
    # if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch the HLS stream. Status code: {response.status_code}")
        status_error += 1
        if status_error == 3:
            exit(0)
        return

    # a subprocess to run ffmpeg
    cmd = [
        "ffmpeg",
        "-i", "-",  # read from stdin
        "-vn",  # disable video
        "-acodec", "copy",  # copy audio codec
        "-f", "mp3",  # output format
        output_file
    ]

    process = Popen(cmd, stdin=PIPE)

    start_time = time.time()
    # read and write the stream content
    try:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                process.stdin.write(chunk)

            # check if duration_sec is exceeded
            if time.time() - start_time > duration_sec:
                break
    except KeyboardInterrupt:
        exit(0)
    finally:
        process.stdin.close()
        process.wait()
    
    # a process to analyze an audio
    p = Process(target=analyze_audio, args=(output_file,))
    p.start()

if __name__ == "__main__":
    config = read_config()
    status_error = 0
    hls_stream_url = config['stream_url']
    
    while(True):
        now = datetime.now()

        output_file = now.strftime("audios/%Y%m%d_%H%M%S.mp3")

        print(output_file)
        duration_sec = config['duration']
        if duration_sec < 10:
            print("Duration can not be less than 10 seconds, please put the higher number in config.json")
            exit(0)

        download_hls_stream(hls_stream_url, output_file, duration_sec)
        
        