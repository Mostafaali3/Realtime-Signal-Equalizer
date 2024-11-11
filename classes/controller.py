from classes.CustomSignal import CustomSignal
from classes.modesEnum import Mode
from classes.frequencyViewer import FrequencyViewer
from classes.equalizingMode import EqualizingMode
from classes.spectrogram import Spectrogram
from classes.viewer import Viewer
class Controller():
    '''
    mode: should be one of the modes in the enum 
    '''
    def __init__(self,old_signal_spectrogram:Spectrogram, new_signal_spectrogram:Spectrogram,  frequency_viewer:FrequencyViewer, old_signal_viewer:Viewer, new_signal_viewer:Viewer, mode:str = Mode.UNIFORM, signal:CustomSignal = None):
        self.__current_signal = signal
        self.mode = mode
        self.old_signal_viewer = old_signal_viewer
        self.new_signal_viewer = new_signal_viewer
        
        self.old_signal_spectrogram = old_signal_spectrogram
        self.new_signal_spectrogram = new_signal_spectrogram
        
        self.frequency_viewer = frequency_viewer
        self.equalizer = EqualizingMode()
        
    def link_two_viewers(sedlf, original, contructed):
        contructed.setXLink(original)
        # contructed.setYLink(original)
        
    def plot_time_domain_signals(self) :
        
        self.old_signal_viewer.clear()
        self.new_signal_viewer.clear()
        
        self.old_signal_viewer.add_signal(self.__current_signal)
        self.new_signal_viewer.add_signal(self.__current_signal)
        self.link_two_viewers(self.old_signal_viewer, self.new_signal_viewer)   
    
        
        
        
    def plot_frequency_viewer(self):
        self.frequency_viewer.current_signal = self.__current_signal
        self.frequency_viewer.plot_freq_domain()
    
    def plot_spectrogram(self):
        if self.__current_signal:
            self.old_signal_spectrogram._current_signal = self.__current_signal
            self.new_signal_spectrogram._current_signal = self.__current_signal
            self.old_signal_spectrogram.plot()
            self.new_signal_spectrogram.plot()
        
    def plot_frequency_boundries(self):
        if(self.mode == Mode.ANIMALS):
            self.frequency_viewer.frequency_boundaries = [10 , 300 , 600 , 1000 , 1700 , 1800 , 2400 , 3400 , 4500 ,6000 , 16000]

        if(self.mode == Mode.UNIFORM):
            self.frequency_viewer.frequency_boundaries = [2205, 4410, 6615, 8820, 11025, 13230, 15435, 17640, 19845, 22050]
        # if(self.mode == Mode.MUSIC):
        #     self.frequency_viewer.frequency_boundaries
        # if(self.mode == Mode.ANIMALS and self.frequency_viewer.view_scale == "Audiogram"):
        #     self.frequency_viewer.frequency_boundaries = [20 , 300 , 600 , 1000 , 1700 , 1800 , 2400 , 3400 , 4500 ,6000 , 16000]
        
    
    def set_current_signal(self, signal:CustomSignal):
        self.__current_signal = signal
        self.equalizer.current_signal = self.__current_signal
        self.plot_frequency_boundries()
        if len(self.__current_signal.original_linear_frequency[0]) == 0:
            self.equalizer.transform()
        self.equalizer.inverse()
        self.plot_frequency_viewer()
        self.plot_spectrogram()
        self.plot_time_domain_signals()
    
    def clear(self):
        pass