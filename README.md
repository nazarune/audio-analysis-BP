# Audio Analysis in OpenLab

Bachelor's thesis project — *"Analýza zvukového obsahu prehrávaného v prostredí OpenLab"* ("Analysis of Audio Content Played in OpenLab") — Technical University of Košice, Faculty of Electrical Engineering and Informatics, Department of Computers and Informatics (KPI), 2024.

**Author:** Nazar Aleksanych
**Supervisor:** Ing. Matúš Sulír, PhD.
**Consultant:** Ing. Tomáš Kormaník

## About

OpenLab is a lab space at KPI, TUKE equipped with spatial microphones that were mostly unused beyond wake-word detection. This project builds a containerized system that streams audio from those microphones and analyzes what's playing — classifying general sound events, transcribing speech to text, and recognizing/analyzing music — then publishes the results to an MQTT broker for use in other applications.

## How it works

The system has two parts:

- **`server/`** — captures audio from a microphone (via `pyaudio`), encodes it in real time with `ffmpeg`, and serves it as an HTTP Live Stream (Flask endpoint `/audio_feed`).
- **`analyzis/`** — the client. Downloads a chunk of the audio stream, runs it through an [Audio Spectrogram Transformer (AST)](https://github.com/YuanGongND/ast) model for general sound classification, and then, depending on the result:
  - if speech is detected → transcribes it to text (Google Speech Recognition, via `SpeechRecognition`)
  - if music is detected → identifies the track with [ShazamIO](https://github.com/shazamio/ShazamIO) and extracts tags (mood, instruments, genre, etc.) with [musicnn](https://github.com/jordipons/musicnn)

  Results from each stage are published as JSON to an MQTT broker (`paho-mqtt`) on separate topics for general classification, music, and transcription.

AST was chosen over [PANNs](https://github.com/qiuqiangkong/audioset_tagging_cnn) after a head-to-head comparison, since it gave faster and more accurate results on the test data.

## Tech stack

Python, Flask, ffmpeg, pyaudio, PyTorch, Audio Spectrogram Transformer, musicnn, ShazamIO, SpeechRecognition, MQTT (paho-mqtt), Docker.

## Setup

### Server

1. Install `ffmpeg` and Python dependencies:
   ```bash
   cd server
   pip install -r requirements.txt
   ```
2. Find your microphone's device index (see `analyzis`/server device-listing script) and set it in `config/config.json`.
3. Run the server:
   ```bash
   python server.py
   ```
4. Verify the stream at `http://localhost:5000/audio_feed`.

> Note: the server is not containerized — Docker's device passthrough only works when host and container share the same OS, which made this impractical for the microphone setup used here.

### Client (analyzis)

Requires Docker.

1. Build the image:
   ```bash
   cd analyzis
   docker build -t audio-client .
   ```
2. Edit `config/config.json` (stream URL, recording duration, speech-recognition locale, MQTT broker/port, MQTT topics).
3. Run the container:
   ```bash
   docker run --publish 5000:5000 \
     --volume ${PWD}/config/config.json:/app/config/config.json \
     --volume ${PWD}/audios:/app/audios \
     --name audio-client audio-client
   ```

## Evaluation (summary)

- **General classification:** ~85–95% accuracy on everyday sounds; some confusions between acoustically similar events (e.g. clapping vs. chopping).
- **Music analysis:** ~85% average classification accuracy on unseen tracks; Shazam correctly identified most test songs; tag/feature prediction was strong for instruments and vocals, weaker for mood.
- **Speech-to-text:** ~98.8% word accuracy for English, ~97.3% for Slovak.

## Known limitations

- The server spawns a new `ffmpeg` process per client request rather than maintaining one continuous stream, which is inefficient with multiple simultaneous clients.
- The client records a fixed-length clip before analyzing it, introducing latency rather than true real-time classification.
- The server could not be containerized due to Docker's microphone/device-passthrough restrictions.

## Full text

The complete thesis (Slovak, with English abstract) covers the theoretical background on digital audio, AST/PANNs/musicnn, and a full system/code appendix — see the [thesis PDF](./thesis.pdf) for details.