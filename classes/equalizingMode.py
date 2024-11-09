from classes.customSignal import CustomSignal
import numpy as np
import matplotlib.pyplot as plt

from classes.frequencyViewer import FrequencyViewer

class EqualizingMode():
    def __init__(self, current_signal:CustomSignal = []):
        self.__current_signal = current_signal
    
    @property
    def current_signal(self):
        return self.__current_signal
    
    @current_signal.setter
    def current_signal(self, new_signal):
        self.__current_signal = new_signal
    
    @property
    def signal_time_magnitude_values(self):
        return self.__signal_time_magnitude_values
    
    @ signal_time_magnitude_values.setter
    def signal_time_magnitude_values(self , new_signal_magnitudes_in_time):
        self.__signal_time_magnitude_values = new_signal_magnitudes_in_time
    
    @property
    def signal_rfft_result(self):
        return self.__signal_rfft_result
    
    @ signal_rfft_result.setter
    def signal_rfft_result(self , new_signal_rfft_result):
        self.__signal_rfft_result = new_signal_rfft_result
        
    @property
    def signal_rfft_result_magnitudes(self):
        return self.__signal_rfft_result_magnitudes
    
    @ signal_rfft_result_magnitudes.setter
    def signal_rfft_result_magnitudes(self , new_signal_rfft_magnitudes):
        self.__signal_rfft_result_magnitudes = new_signal_rfft_magnitudes
        
    @property
    def signal_frequencies(self):
        return self.__signal_frequencies
    
    @ signal_frequencies.setter
    def signal_frequencies(self , new_signal_frequencies):
        self.__signal_frequencies = new_signal_frequencies
        
    @property
    def signal_rfft_result_phase(self):
        return self.__signal_rfft_result_phase
    
    @ signal_rfft_result_phase.setter
    def signal_rfft_result_phase(self , new_signal_rfft_result_phase):
        self.__signal_rfft_result_phase = new_signal_rfft_result_phase
    
            
    
        
    def transform(self):
        '''
        this function is to make the frequency transform on the data given 
        '''
        self.signal_time_magnitude_values = self.current_signal.original_signal[1]
        self.current_signal.original_linear_frequency[0] = np.fft.rfftfreq(len(self.signal_time_magnitude_values) , 1 / self.current_signal.signal_sampling_rate)
        self.current_signal.original_linear_frequency[1] = np.fft.rfft(self.signal_time_magnitude_values)
        self.current_signal.new_linear_frequency[0] = np.fft.rfftfreq(len(self.signal_time_magnitude_values) , 1 / self.current_signal.signal_sampling_rate)
        self.current_signal.new_linear_frequency[1] = np.fft.rfft(self.signal_time_magnitude_values)
    
    def inverse(self):
        '''
        this function is to restore the signal from its frequencies including the shift
        '''
        signal_rfft_result_magnitudes = np.abs(self.current_signal.new_linear_frequency[1])
        signal_rfft_result_phase = np.angle(self.current_signal.new_linear_frequency[1])
        signal_rfft_components = signal_rfft_result_magnitudes * np.exp(1j * signal_rfft_result_phase)
        self.current_signal.reconstructed_signal[1] = np.fft.irfft(signal_rfft_components)
        # plt.plot( self.current_signal.reconstructed_signal[0], self.current_signal.reconstructed_signal[1])
        # plt.show()
        
    def equalize(self, pairs_of_freq_ranges, factor):
        '''
        this function is to amplify or reduce the amplitude for the data in a specific given region
        '''
        signal_rfft_result_magnitudes = np.abs(self.current_signal.original_linear_frequency[1])
        signal_rfft_result_phase = np.angle(self.current_signal.original_linear_frequency[1])
        for freq_range in pairs_of_freq_ranges:
            lower_bound_index = (np.abs(self.current_signal.original_linear_frequency[0] - freq_range[0])).argmin()
            upper_bound_index = (np.abs(self.current_signal.original_linear_frequency[0] - freq_range[1])).argmin()
            equalized_signal_magnitudes = signal_rfft_result_magnitudes[lower_bound_index: upper_bound_index] * factor
            equalized_signal_phase = signal_rfft_result_phase[lower_bound_index: upper_bound_index]
            equalized_signal_components = equalized_signal_magnitudes * np.exp(1j * equalized_signal_phase)
            self.current_signal.new_linear_frequency[1][lower_bound_index : upper_bound_index] =equalized_signal_components
            
# def test_signal_maker():
#     sampling_rate = 1000
#     duration = 1
#     t = np.linspace(0, duration, sampling_rate * duration, endpoint=False)
#     frequency1 = 2
#     frequency2 = 4
#     frequency3 = 10
#     frequencies = [frequency1 , frequency2 ,frequency3]
#     signal = 0.5 * np.sin(2 * np.pi * frequency1 * t) + 0.3 * np.sin(2 * np.pi * frequency2 * t) + 0.9 * np.sin(2 * np.pi * frequency3 * t)

#     return [t , signal] ,frequencies

# test_signal = test_signal_maker()
# signal = CustomSignal(test_signal[0][0] , test_signal[0][1])
# signal.frequency_limits['cat'] = [(1,3) , (3,5)]
# signal.frequency_limits['horse'] = [(9,11)]
# equalize = EqualizingMode(signal)
# equalize.transform()
# equalize.equalize(signal.frequency_limits['horse'] , 2)
# equalize.equalize(signal.frequency_limits['cat'] , 0)
# equalize.inverse()
# freq_viewer = FrequencyViewer(signal)
# freq_viewer.plot_freq_domain()