import demucs.separate
import os, shutil
from pathlib import Path
import subprocess

MODEL = "mdx_extra"

def main(root: str):
    audio_file = f"{root}/stereo.wav"

    demucs.separate.main(["-n", MODEL, "--two-stems", "vocals", "--shifts", "10", "-o", root, f"{root}/song.wav"])
    os.rename(f"{root}/mdx_extra/song/vocals.wav", audio_file)
    # shutil.rmtree(f"{root}/{MODEL}")

    if Path(audio_file).exists():
        subprocess.call(f"ffmpeg -hide_banner -loglevel error -i '{audio_file}' -ac 1 {root}/audio.wav", shell=True)
        os.remove(audio_file)
    else:
        print("Failed to extract vocals.")

if __name__ == "__main__":
    main("song")