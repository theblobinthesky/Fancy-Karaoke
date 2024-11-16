import numpy as np
from soundfile import SoundFile
import soundfile as sf
import json

def get_soundfile_metadata(file: str):
    with SoundFile(file, 'r') as sound:
        return sound.frames

def get_line_endings(root: str, c: int, chapter):
    timestamps = [0]
    sum_of_individuals = 0 
    for l, line in enumerate(chapter["lines"]):
        _, filename = line["text"], line["filename"]
        frames = get_soundfile_metadata(f"{root}/{filename}.wav")
        sum_of_individuals += frames
        timestamps.append(sum_of_individuals)

    frames = get_soundfile_metadata(f"{root}/tts-joins/{c}.wav")
    signal, samplerate = sf.read(f"{root}/tts-joins/{c}.wav")
    if signal.shape[0] != sum_of_individuals:
        raise ValueError("Concatenation modified padding somewhere.")

    # Convert to percentages.
    timestamps = [float(t) / sum_of_individuals for t in timestamps] 
    len_sec = float(signal.shape[0]) / samplerate
    return timestamps, len_sec

def get_t_in_audios(root: str, c: int, timestamps):
    time_warp = np.load(f"{root}/tts-joins/{c}.tw")
    t_in_audios = []
    for t in timestamps:
        print(f"{t=}, {time_warp=}")
        nonzero = np.nonzero(time_warp[:, 1] <= t)[0]
        idx_in_ft = 0 if len(nonzero) == 0 else nonzero[-1]
        t_in_audio = time_warp[idx_in_ft, 0]
        t_in_audios.append(t_in_audio)

    return t_in_audios


def main(root: str):
    print("Syncing lyrics with audio...")

    with open(f"{root}/tts.json", "r") as file:
        chapters = json.load(file)

    c = 0
    chapter = chapters[c]

    timestamps, audio_len_sec = get_line_endings(root, c, chapter)
    t_in_audios = get_t_in_audios(root, c, timestamps)

    syncs = []
    for l, line in enumerate(chapter["lines"]):
        begin_in_sec = t_in_audios[l] * audio_len_sec
        end_in_sec = t_in_audios[l + 1] * audio_len_sec

        num_words = len(line["text"].split(" "))
        words_begin = list(np.linspace(0, end_in_sec - begin_in_sec, num_words + 1))[:-1]
        words_end = list(np.linspace(0, end_in_sec - begin_in_sec, num_words + 1))[1:]

        sync = {"line": line["text"], "offset": begin_in_sec, "words_begin": words_begin, "words_end": words_end}
        syncs.append(sync)

    with open(f"{root}/syncs.json", "w") as file:
        json.dump(syncs, file, indent=2)

if __name__ == "__main__":
    main("song")