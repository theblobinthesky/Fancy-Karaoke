# See https://medium.com/@derutycsl/intuitive-understanding-of-mfccs-836d36a1f779
# See https://en.wikipedia.org/wiki/Mel_scale
# See https://en.wikipedia.org/wiki/Mel-frequency_cepstrum

import soundfile as sf
import numpy as np
import librosa
import scipy
from tqdm import tqdm
from pathlib import Path

NFFT = 1024
NMELS = 16

def resample_and_downscale_using_mel_scale(pow_spectrum: np.ndarray, sr: int):
    mel_filter = librosa.filters.mel(sr=sr, n_fft=NFFT, n_mels=NMELS)
    mel_spectrum = np.dot(mel_filter, pow_spectrum)

    # if np.isnan(mel_spectrum).any():
    #    print(f"nans: {np.isinf(pow_spectrum).any()}")

    return mel_spectrum

def compute_mel_cepstrum(stft: np.ndarray, samplerate: int):
    # Include the 0-frequency (constant offset), don't have the negative frequencies since
    # for the fft of real signals the negative frequencies are redundant. 
    num_pos_freq = stft.shape[0] // 2 + 1 

    pow_spectrum = np.abs(stft) / num_pos_freq
    log_pow_spectrum = np.log(pow_spectrum)
    mel_log_pow_spectrum = resample_and_downscale_using_mel_scale(log_pow_spectrum, samplerate)
    mel_cepstrum = scipy.fftpack.dct(mel_log_pow_spectrum)

    return mel_cepstrum

def compute_features(signal: np.ndarray, samplerate: int):
    f, t, zxx = scipy.signal.stft(signal, nfft=NFFT, window="hann")
    features = np.zeros((zxx.shape[1], NMELS))
    for i in tqdm(range(zxx.shape[1])):
        features[i] = compute_mel_cepstrum(zxx[:, i], samplerate)

    features[np.isnan(features)] = 0.0

    return features

def load_features(file: str):
    print(f"Loading features of '{file}'")
    signal, samplerate = sf.read(file)
    if len(signal.shape) != 1:
        raise ValueError("Only mono audio can be processed.")

    return compute_features(signal, samplerate)

def load_and_save_features(file: str):
    features = load_features(file)

    path = str(Path(file).parent.joinpath(Path(file).stem))
    ft_path = f"{path}.ft"
    with open(ft_path, "wb") as file:
        np.save(file, features)

def main(root: str):
    audio_wav = f"{root}/audio.wav"
    tts_wav = f"{root}/tts.wav"
    # tts_wavs = [str(path) for path in Path(f"{root}/tts").glob("*.wav")]

    load_and_save_features(audio_wav)

    for tts_join in Path(f"{root}/tts-joins").glob("*.wav"):
        load_and_save_features(str(tts_join))

if __name__ == "__main__":
    main("song")