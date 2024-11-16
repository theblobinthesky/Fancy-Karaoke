import shutil
from pathlib import Path
import audio, lyrics, tts, feature_mel_freq_cepstrum as feature, time_warp, seperate, sync

root = "song"
shutil.rmtree(root, ignore_errors=True)
Path(root).mkdir()

lyrics.main(root)
audio.main(root)
tts.main(root)
seperate.main(root)
feature.main(root)
time_warp.main(root)
sync.main(root)