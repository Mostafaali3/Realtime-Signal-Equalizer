import numpy as np
from scipy.io import wavfile
from scipy.signal import stft, istft, butter, lfilter

class WeinerFilter():
    def init(self):
        super().init()

    def iterative_wiener_filter(self, noisy_signal, noise_signal, fs, n_fft=1024, overlap=None, iterations=3, spectral_floor=0.1):
        """
        Apply an iterative Wiener filter for enhanced noise removal.

        Parameters:
            noisy_signal (numpy array): The noisy audio signal.
            noise_signal (numpy array): A noise-only segment for estimation.
            fs (int): Sampling frequency of the signals.
            n_fft (int): Number of FFT points.
            overlap (int): Overlap between segments. If None, set to half of n_fft.
            iterations (int): Number of iterative filtering steps.
            spectral_floor (float): Minimum filter gain to preserve weak signal components.

        Returns:
            denoised_signal (numpy array): The denoised audio signal (1D array).
        """
        # Default to 50% overlap if not provided
        if overlap is None:
            overlap = n_fft // 2

        # Ensure noverlap is less than nperseg
        if overlap >= n_fft:
            raise ValueError('noverlap must be less than nperseg.')

        # Compute STFT
        f, t, noisy_stft = stft(noisy_signal, fs, nperseg=n_fft, noverlap=overlap)
        _, _, noise_stft = stft(noise_signal, fs, nperseg=n_fft, noverlap=overlap)

        # Estimate noise PSD
        noise_psd = np.mean(np.abs(noise_stft) ** 2, axis=-1, keepdims=True)

        # Iterative Wiener filtering
        filtered_stft = noisy_stft
        for _ in range(iterations):
            noisy_psd = np.abs(filtered_stft) ** 2
            wiener_filter = np.maximum(noisy_psd / (noisy_psd + noise_psd), spectral_floor)
            filtered_stft = wiener_filter * noisy_stft

        # Inverse STFT
        _, denoised_signal = istft(filtered_stft, fs, nperseg=n_fft, noverlap=overlap)

        # Ensure the returned signal is 1D
        return denoised_signal.ravel()


        
    def highpass_filter(self, signal, fs, cutoff=50, order=5):
        """Apply a high-pass filter to remove low-frequency noise."""
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return lfilter(b, a, signal)


weiner = WeinerFilter()

fs, noisy_signal = wavfile.read("./data_new/Wiener/mix.wav")
fs, noise_signal = wavfile.read("./data_new/Wiener/clapping.wav")

# Ensure signals are mono
if noisy_signal.ndim > 1:
    noisy_signal = noisy_signal[:, 0]
if noise_signal.ndim > 1:
    noise_signal = noise_signal[:, 0]

# Apply the improved iterative Wiener filter
denoised_signal = weiner.iterative_wiener_filter(noisy_signal, noise_signal, fs)
wavfile.write('denoised_audio_iterative.wav', fs, denoised_signal.astype(np.int16))