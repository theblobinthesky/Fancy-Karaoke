import yt_dlp
from pathlib import Path
import os
import subprocess

def download_youtube_mp3(url: str, root: str) -> None:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Find the downloaded mp3 file
    info_dict = ydl.extract_info(url, download=False)
    title = info_dict.get('title', 'downloaded_audio')
    audio_file = f"{title}.wav"

    if Path(audio_file).exists():
        subprocess.call(f"ffmpeg -hide_banner -loglevel error -i '{audio_file}' -ac 1 {root}/audio.wav", shell=True)
        os.remove(audio_file)
    else:
        print("Failed to download MP3.")

def main(root: str):
    youtube_url: str = input("Enter YouTube URL: ")
    download_youtube_mp3(youtube_url, root)