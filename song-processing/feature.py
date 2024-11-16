# See https://medium.com/@derutycsl/intuitive-understanding-of-mfccs-836d36a1f779
# See https://en.wikipedia.org/wiki/Mel_scale
# See https://en.wikipedia.org/wiki/Mel-frequency_cepstrum
# See https://haythamfayek.com/2016/04/21/speech-processing-for-machine-learning.html

import soundfile as sf
import numpy as np
import librosa
import scipy
from tqdm import tqdm
from pathlib import Path

NFFT = 512
NMELS = 40
NKEEPS = 12

def resample_and_downscale_using_mel_scale(pow_spectrum: np.ndarray, sr: int):
    mel_filter = librosa.filters.mel(sr=sr, n_fft=NFFT, n_mels=NMELS)
    mel_spectrum = np.dot(mel_filter, pow_spectrum)
    return mel_spectrum

def compute_mel_cepstrum(stft: np.ndarray, samplerate: int):
    # pow_spectrum = np.abs(stft) / num_pos_freq
    pow_spectrum = (np.abs(stft) ** 2) / NFFT
    pow_spectrum[pow_spectrum == 0] = np.finfo(float).eps # Avoid log(0)==Nan.
    # log_pow_spectrum = np.log(pow_spectrum)
    mel_pow_spectrum = resample_and_downscale_using_mel_scale(pow_spectrum, samplerate)
    dct = scipy.fftpack.dct(mel_pow_spectrum, type=2, norm="ortho")
    mel_cepstrum = dct[1:(NKEEPS + 1)] # Only keep the first couple of coefficients, since fine details don't matter.

    return mel_cepstrum

def compute_features(signal: np.ndarray, samplerate: int):
    f, t, zxx = scipy.signal.stft(signal, nfft=NFFT, window="hann")
    features = np.zeros((zxx.shape[1], NKEEPS))
    for i in tqdm(range(zxx.shape[1])):
        feature = compute_mel_cepstrum(zxx[:, i], samplerate)

        # Normalize feature.
        eature = (feature - np.mean(feature)) / np.linalg.norm(feature)
        features[i] = feature

    return features

def load_features(file: str):
    print(f"Loading features of '{file}'")
    signal, samplerate = sf.read(file)
    if len(signal.shape) != 1:
        raise ValueError("Only mono audio can be processed.")

    return compute_features(signal, samplerate)

def load_and_save_features(file: str):
    features = load_features(file)

    ft_path = Path(file).with_suffix(".ft")
    with open(ft_path, "wb") as file:
        np.save(file, features)

def main(root: str):
    audio_wav = f"{root}/audio.wav"
    load_and_save_features(audio_wav)

    for tts_join in Path(f"{root}/tts-joins").glob("*.wav"):
        load_and_save_features(str(tts_join))

if __name__ == "__main__":
    main("song")