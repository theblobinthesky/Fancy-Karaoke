import shutil
from pathlib import Path
import audio, lyrics, tts

root = "song"
shutil.rmtree(root, ignore_errors=True)
Path(root).mkdir()

lyrics.main(root)
audio.main(root)
tts.main(root)
feature.main(root)