FROM python:3.7.17-slim

WORKDIR /app

COPY . /app

RUN apt-get update \ 
    && apt-get install -y ffmpeg portaudio19-dev gcc libc-dev alsa-utils libblas-dev liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt --no-deps --no-cache-dir

RUN pip install --no-deps --no-cache-dir torch==1.8.1+cpu torchvision==0.9.1+cpu torchaudio==0.8.1 -f https://download.pytorch.org/whl/torch_stable.html

CMD ["python", "client.py"]