from gtts import gTTS
from pathlib import Path
import shutil
import json
import re

def load_lines(name: str):
    with open(name, 'r') as file:
        lines = file.readlines()

    lines = [line.strip("\n") for line in lines]
    return lines

def get_chapters(lines: list[str]):
    chapters = []
    textToFile = {}
    lastLines = None
    for i, line in enumerate(lines):
        if line.startswith("["):
            chapter = line.strip("[]")
            chapters.append({"chapter": chapter, "lines": []})
            lastLines = chapters[-1]["lines"]
        else:
            temp = line
            line = re.sub("\(.*\)", "", line)
            line = line.replace("\"", "")
            line = line.replace("'", "")
            line = line.strip()

            if line == "": continue

            if textToFile.__contains__(line):
                # Use the already downloaded file.
                lastLines.append({"file": textToFile[line], "text": line})
            else:
                file = f"tts/{i}.mp3"
                textToFile[line] = file
                lastLines.append({"file": file, "text": line})

    return chapters, textToFile.items()

def run_tts(root: str, downloads):
    cache = {}

    for (text, file) in downloads:
        print(f"TTS on '{text}'...")
        tts = gTTS(text, lang='en-US', slow=True)
        tts.save(f"{root}/{file}")

def main(root: str):
    shutil.rmtree(f"{root}/tts", ignore_errors=True)
    Path(f"{root}/tts").mkdir()

    lines = load_lines(f"{root}/lyrics.txt")
    chapters, downloads = get_chapters(lines)

    with open(f"{root}/tts.json", "w") as file:
        json.dump(chapters, file, indent=2)

    run_tts(root, downloads)