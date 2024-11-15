from tslearn.metrics import dtw_path
import numpy as np

root = "song"
audio = np.load(f"{root}/audio.ft")
tts = np.load(f"{root}/tts-joins/1.ft")

# See https://medium.com/@markstent/dynamic-time-warping-a8c5027defb6
# See https://rtavenar.github.io/blog/dtw.html

optimal_path, dtw_score = dtw_path(audio, tts)
for mapping in optimal_path:
    print(mapping[0], mapping[1])