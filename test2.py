import numpy as np


def wiener_filter(audio_data,sampling_rate ,noise_estimate_duration=4):
    """
    Apply Wiener filtering to remove uniform background noise from speech audio.
    
    Parameters:
        audio_path (str): Path to the WAV file
        noise_estimate_duration (float): Duration in seconds to use for noise estimation
                                        (typically from the beginning of the file)
    
    Returns:
        tuple: (cleaned_audio, sampling_rate)
    """
    audio_data = audio_data.astype(np.float32)

    # Estimate noise spectrum from the first segment
    noise_start = int(6 * sampling_rate)
    noise_end = int(11* sampling_rate)
    noise_segment = audio_data[noise_start:noise_end]
    
    # Compute noise power spectrum
    noise_fft = np.fft.fft(noise_segment)
    noise_power = np.abs(noise_fft) ** 2
    noise_power = np.mean(noise_power)
    
    # Process the signal in overlapping frames
    frame_length = 2048
    hop_length = frame_length // 2
    window = np.hanning(frame_length)
    
    # Prepare output array
    cleaned_audio = np.zeros_like(audio_data)
    epsilon = 1e-10

    for i in range(0, len(audio_data) - frame_length, hop_length):
        frame = audio_data[i:i + frame_length]
        windowed_frame = frame * window
        frame_fft = np.fft.fft(windowed_frame)
        frame_power = np.abs(frame_fft) ** 2

        # Improved Wiener filter with regularization
        wiener_filter = 0.9 * np.maximum(0, (frame_power - noise_power) / (frame_power + noise_power + epsilon))
        filtered_frame = frame_fft * wiener_filter
        cleaned_frame = np.real(np.fft.ifft(filtered_frame))

        cleaned_audio[i:i + frame_length] += cleaned_frame * window
    
    # Normalize output
    cleaned_audio = cleaned_audio / np.max(np.abs(cleaned_audio))
    
    return cleaned_audio