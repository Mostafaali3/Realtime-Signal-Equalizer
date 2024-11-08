from classes.customSignal import CustomSignal
from classes.modesEnum import Mode
from classes.frequencyViewer import FrequencyViewer
from classes.equalizingMode import EqualizingMode
from classes.spectrogram import Spectrogram

class Controller():
    '''
    mode: should be one of the modes in the enum 
    '''
    def __init__(self,old_signal_spectrogram:Spectrogram, new_signal_spectrogram:Spectrogram,  frequency_viewer:FrequencyViewer,  mode:str = Mode.ANIMALS, signal:CustomSignal = None):
        self.__current_signal = signal
        self.mode = mode
        self.old_signal_viewer = None
        self.new_signal_viewer = None
        self.old_spectrogram = None
        self.new_spectrogram = None
        self.old_signal_spectrogram = old_signal_spectrogram
        self.new_signal_spectrogram = new_signal_spectrogram
        
        self.frequency_viewer = frequency_viewer
        self.equalizer = EqualizingMode()
        
    def plot_frequency_viewer(self):
        self.frequency_viewer.current_signal = self.__current_signal
        self.frequency_viewer.plot_freq_domain()
    
    def plot_spectrogram(self):
        pass
    
    def set_current_signal(self, signal:CustomSignal):
        self.__current_signal = signal
        self.equalizer.current_signal = self.__current_signal
        if len(self.__current_signal.original_linear_frequency[0]) == 0:
            self.equalizer.transform()
        self.plot_frequency_viewer()
    
    def clear(self):
        pass