from tslearn.metrics import dtw_subsequence_path
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json

def main(root: str):
    tts_file = f"{root}/tts.json"
    with open(tts_file, "r") as file:
        chapters = json.load(file)
    
    audio_full = np.load(f"{root}/audio.ft")
    total_audio_samples_processed = 0  # To track cumulative processed samples
    
    audio = audio_full.copy()  # Create a copy to manipulate

    for c, chapter in tqdm(enumerate(chapters), desc="Time warping against tts-joins"):
        ft_path = f"{root}/tts-joins/{c}.ft"
        ft = np.load(ft_path)
        
        # Compute DTW subsequence path between the current audio and ft.
        # Ft is a short segment of audio.
        optimal_path, _ = dtw_subsequence_path(ft, audio)
        optimal_path = np.array(optimal_path)

        # Adjust the indices in optimal_path to refer to the original audio
        # optimal_path[:, 0] += total_audio_samples_processed

        # Get the last matched index in audio
        # last_audio_sample = int(optimal_path[-1][1])

        # Update total processed samples
        # total_audio_samples_processed += last_audio_sample + 1

        # Update the audio array by removing the matched segment
        # audio = audio[(last_audio_sample - total_audio_samples_processed + 1):]

        # Convert the optimal path to percentages relative to the original audio and ft lengths
        optimal_path = np.stack([optimal_path[:, 1], optimal_path[:, 0]], axis=1)
        optimal_path = optimal_path.astype("float64")
        optimal_path[:, 0] /= audio_full.shape[0]
        optimal_path[:, 1] /= ft.shape[0]

        # Save the time-warping path
        tw_path = Path(ft_path).with_suffix(".tw")
        with open(tw_path, "wb") as file:
            np.save(file, optimal_path)

if __name__ == "__main__":
    main("song")