from tslearn.metrics import dtw_path
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json

def main(root: str):
    tts_file = f"{root}/tts.json"
    with open(tts_file, "r") as file:
        chapters = json.load(file)

    audio = np.load(f"{root}/audio.ft")

    for c, chapter in tqdm(enumerate(chapters), desc="Time warping against tts-joins"):
        ft_path = f"{root}/tts-joins/{c}.ft"
        ft = np.load(ft_path)

        # See https://medium.com/@markstent/dynamic-time-warping-a8c5027defb6
        # See https://rtavenar.github.io/blog/dtw.html
        optimal_path, dtw_score = dtw_path(audio, ft)
        optimal_path = np.array(optimal_path)

        # lastAudioSample = optimal_path[-1][0]
        # audio = audio[lastAudioSample + 1:]
        # print(audio.shape)

        tw_path = Path(ft_path).with_suffix(".tw")
        with open(tw_path, "wb") as file:
            np.save(file, optimal_path)
        
        chapters[c]["audio_len"] = audio.shape[0]
        chapters[c]["ft_len"] = ft.shape[0]

    with open(tts_file, "w") as file:
        json.dump(chapters, file, indent=2)

if __name__ == "__main__":
    main("song")