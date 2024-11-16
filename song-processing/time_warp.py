from tslearn.metrics import dtw, dtw_path
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json

FT_BEGIN = 128
AUDIO_BEGIN = 224

def main(root: str):
    tts_file = f"{root}/tts.json"
    with open(tts_file, "r") as file:
        chapters = json.load(file)

    audio = np.load(f"{root}/audio.ft")

    for c, chapter in tqdm(enumerate(chapters), desc="Time warping against tts-joins"):
        ft_path = f"{root}/tts-joins/{c}.ft"
        ft = np.load(ft_path)

        import matplotlib.pyplot as plt

        # Find the padding at the start of the audio features.
        begin_padding = 0
        min_no_pad_score = float("inf")
        scores = []
        indices = []
        for i in range(audio.shape[0] - AUDIO_BEGIN):
            no_pad_score = dtw(audio[i:i+AUDIO_BEGIN], ft[:FT_BEGIN])
            scores.append(no_pad_score)
            indices.append(i)
            if no_pad_score < min_no_pad_score:
                begin_padding = i
                min_no_pad_score = no_pad_score

        # Plot the no pad scores
        plt.figure(figsize=(10, 6))
        plt.plot(indices, scores, marker='o')
        plt.xlabel('Padding (i)')
        plt.ylabel('DTW Score')
        plt.title('DTW Scores vs Padding')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Remove the initial padding using the optimal starting index.
        audio = audio[begin_padding:]

        # See https://medium.com/@markstent/dynamic-time-warping-a8c5027defb6
        # See https://rtavenar.github.io/blog/dtw.html
        optimal_path, dtw_score = dtw_path(audio, ft, global_constraint="itakura")
        optimal_path = np.array(optimal_path)
        optimal_path[:, 0] += begin_padding

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