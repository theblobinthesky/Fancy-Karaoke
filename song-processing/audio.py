import yt_dlp
from pathlib import Path

def download_youtube_mp3(url: str, root: str) -> None:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Find the downloaded mp3 file
    info_dict = ydl.extract_info(url, download=False)
    title = info_dict.get('title', 'downloaded_audio')
    mp3_filename = f"{title}.mp3"

    if Path(mp3_filename).exists():
        Path(mp3_filename).rename(f"{root}/audio.mp3")
    else:
        print("Failed to download MP3.")

def main(root: str):
    youtube_url: str = input("Enter YouTube URL: ")
    download_youtube_mp3(youtube_url, root)