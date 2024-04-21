import os
import time

startTime = time.time()
os.system("python inference.py --model_path ../../pretrained_models/audioset_10_10_0.4593.pth --audio_path LDoXsip0BEQ_000177.flac")
print(f"{time.time()-startTime}s spent")