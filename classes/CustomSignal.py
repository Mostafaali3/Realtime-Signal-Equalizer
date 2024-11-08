from copy import deepcopy

class CustomSignal():
    def __init__(self, data_x, data_y, frequency_limits = [], linear_frequency = [[],[]]):
        self.__original_signal = [data_x, data_y]
        self.__reconstructed_signal = deepcopy(self.original_signal)
        self.__frequency_limits = frequency_limits
        self.__original_linear_frequency = linear_frequency
        self.__new_linear_frequency = linear_frequency
        self.__signal_sampling_rate = 1 / (self.original_signal[0][1] - self.original_signal[0][0])
        
    @property
    def original_signal(self):
        return self.__original_signal
    
    @ original_signal.setter
    def original_signal(self, new_signal):
        if isinstance(new_signal, list) and len(new_signal) == 2:
            self.__original_signal = new_signal
            
    @property
    def reconstructed_signal(self):
        return self.__reconstructed_signal
    
    @ reconstructed_signal.setter
    def reconstructed_signal(self, new_signal):
        if isinstance(new_signal, list) and len(new_signal) == 2:
            self.__reconstructed_signal = new_signal
    
    @property
    def frequency_limits(self):
        return self.__frequency_limits
    
    @ frequency_limits.setter
    def frequency_limits(self, new_signal):
        if isinstance(new_signal, list) and len(new_signal) == 1:
            self.__frequency_limits = new_signal
    
    @property
    def original_linear_frequency(self):
        return self.__original_linear_frequency
    
    @ original_linear_frequency.setter
    def original_linear_frequency(self, new_signal):
        if isinstance(new_signal, list) and len(new_signal) == 2:
            self.__original_linear_frequency = new_signal
    
    @property
    def new_linear_frequency(self):
        return self.__new_linear_frequency
    
    @ new_linear_frequency.setter
    def new_linear_frequency(self, new_signal):
        if isinstance(new_signal, list) and len(new_signal) == 2:
            self.__new_linear_frequency = new_signal
    
    @property
    def signal_sampling_rate(self):
        return self.__signal_sampling_rate        
    