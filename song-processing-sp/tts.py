from gtts import gTTS
from pathlib import Path
import shutil
import json
import re
import subprocess

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
            line = re.sub(r"\(.*\)", "", line)
            line = line.replace("\"", "")
            line = line.replace("'", "")
            line = line.strip()

            if line == "": continue

            if textToFile.__contains__(line):
                # Use the already downloaded file.
                lastLines.append({"filename": textToFile[line], "text": line})
            else:
                filename = f"tts/{i}"
                textToFile[line] = filename
                lastLines.append({"filename": filename, "text": line})

    # Remove empty chapters
    chapters = [chapter for chapter in chapters if len(chapter["lines"]) > 0]

    return chapters, textToFile.items()

def run_tts(root: str, lang: str, downloads):
    cache = {}
    wavs = []

    for (text, file) in downloads:
        print(f"TTS on '{text}'.")
        tts = gTTS(text, lang=lang)
        wav = f"{root}/{file}.wav"
        tts.save(wav)
        wavs.append(wav)

def join_tts(root: str, chapters):
    for c, chapter in enumerate(chapters):
        print(f"TTS Join on chapter {c}")
        wavs = []
        for line in chapter["lines"]:
            filename = line["filename"]
            wavs.append(f"{root}/{filename}.wav")

        # Write out the list of files that should be joined.
        joinlist = "\n".join([f"file '{Path(wav).relative_to(root)}'" for wav in wavs])
        join_path = f"{root}/joinlist.txt"
        with open(join_path, "w") as file:
            file.write(joinlist)

        # Join them.
        cmd = f"ffmpeg -hide_banner -loglevel error -f concat -i {root}/joinlist.txt -c copy {root}/tts-joins/{c}.wav"
        subprocess.call(cmd, shell=True)

        # Delete the list.
        Path(join_path).unlink(missing_ok=True)

def main(root: str):
    shutil.rmtree(f"{root}/tts", ignore_errors=True)
    Path(f"{root}/tts").mkdir()

    shutil.rmtree(f"{root}/tts-joins", ignore_errors=True)
    Path(f"{root}/tts-joins").mkdir()

    lines = load_lines(f"{root}/lyrics.txt")
    chapters, downloads = get_chapters(lines)

    with open(f"{root}/tts.json", "w") as file:
        json.dump(chapters, file, indent=2)

    lang = input("Language (default: en-US): ")
    lang = lang if lang != "" else "en-US"
    print(f"Language: {lang}")
    run_tts(root, lang, downloads)

    join_tts(root, chapters)

if __name__ == "__main__":
    main("song")