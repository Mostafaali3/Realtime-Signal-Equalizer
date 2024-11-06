import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import pandas as pd
import numpy as np
from math import inf
import struct
import pyaudio
import librosa
import sounddevice as sd

class Waveform:
    def __init__(self, file_path, wave_type = 'audio', mono = True, sampling_rate = None):
        if wave_type == 'audio':
            self.y_array, self.sampling_rate = librosa.load(file_path, sr=sampling_rate, mono=mono)
            self.duration = len(self.y_array) / self.sampling_rate
            self.x_array = np.linspace(0, self.duration, len(self.y_array))

        pass
    
    def len(self):
        return len(self.y_array)
        

class CustomSignal(Waveform):
    def __init__(self, signal, color = "r", label = "signal", visability=True):
        super().__init__()
        self.__color = color
        self.__label = label
        self.__signal = signal
        self.__visability = visability
        
    @property
    def color(self):
        return self.__color
    
    @property
    def label(self):
        return self.__label
    
    @property
    def signal(self):
        return self.__signal
    
    @property
    def visability(self):
        return self.__visability
    
    @signal.setter
    def signal(self, value):
        if isinstance(value,list):
            self.__signal = value
        else:
            raise Exception("the signal must be a list")
        
    @color.setter
    def color(self, value): ## this function could be modified accourding to the gui
        if isinstance(value,str):
            self.__color = value
        else :
            raise Exception("the color must be a string")  
        
    @label.setter
    def label(self, value): 
        if isinstance(value,str):
            self.__label = value
        else :
            raise Exception("the label must be a string")  
        
    @visability.setter
    def visability(self, value): 
        if isinstance(value,bool):
            self.__visability = value
        else :
            raise Exception("the visability must be a boolean")  
        
    def __len__(self):
        return len(self.__signal)
        
    def get_mean():
        pass
    
    def get_std():
        pass 
    
    def get_min():
        pass 
    
    def get_max():
        pass
    
    def get_duration():
        pass  
    
        

class Viewer(pg.PlotWidget):
    def __init__(self):
        super().__init__()
        self.__channels = []
        self.__rewind_state = False
        self.__cine_speed = 60
        self.__zoom = 1
        
        self.x_axis = []
        
        self.drag_active = False  
        
        self.play_state = False
        
        self.viewBox = self.getViewBox()
        
        self.y_axis_scroll_bar_enabled = False 
        
        self.counter = 0
        self.time_window = 1000
        
        self.max_signals_value = -inf
        self.min_signals_value = inf    
        
        # self.scrolling_in_y_axis = False
        
        ## range trackers
        self.x_range_tracker_min, self.x_range_tracker_max = 0,1000
        self.y_range_tracker_min, self.y_range_tracker_max = 0,1000
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_signal)
        # self.play()
    
    def update_signal(self):
        
        if self.time_window + self.counter < len(self.x_axis):
            self.counter += 20
            # print(f"{self.viewRange()} range in updating")
        else:
            if self.__rewind_state:
                self.counter = 0
        self.setXRange(min(self.x_axis[self.counter:self.counter + self.time_window]), max(self.x_axis[self.counter:self.counter + self.time_window])  )
        
        min_interval_value = inf
        max_interval_value = -inf
        for channel in self.__channels:
            if self.counter + self.time_window > len(channel):
                continue
            min_channel_interval_value = min(channel.signal[self.counter:self.counter + self.time_window])
            if min_channel_interval_value < min_interval_value:
                min_interval_value = min_channel_interval_value
            max_channel_interval_value = max(channel.signal[self.counter:self.counter + self.time_window])
            if max_channel_interval_value > max_interval_value:
                max_interval_value = max_channel_interval_value

    def add_channel(self , new_channel):
        if isinstance(new_channel , CustomSignal):
            self.__channels.append(new_channel)
            self.x_axis = list(range(max([len(signal) for signal in self.__channels]))) ## max len in the signals imported
            for channel in self.__channels:
                self.plot( [i for i in  range(len(channel.signal))] ,channel.signal, pen = pg.mkPen(color = channel.color))## pass the x_axis from the length of the signal
                print(channel.color)
                if min(channel.signal) < self.min_signals_value:
                    self.min_signals_value = min(channel.signal)
                if max(channel.signal) > self.max_signals_value:
                    self.max_signals_value = max(channel.signal)
        else:
            raise Exception("The new channel must be of class CustomSignal")
        
    def play(self):
        if self.play_state == False:
            self.play_state = True
            
            # add a line that strats playing audio
            
            self.timer.start(self.__cine_speed)
            # print(self.__cine_speed)

        self.viewBox.setMouseEnabled(x = True, y =False)
        self.viewBox.enableAutoRange(x=False, y=True)
        self.viewBox.setAutoVisible(x=False, y=True)
            # self.setYRange(self.viewRange()[1][0], self.viewRange()[1][1])
        self.setXRange(self.viewRange()[0][0]+50, self.viewRange()[0][0]+1000)
        self.counter = int(max(0,self.viewRange()[0][0]))
            # print(f"{self.counter} this is counter from the play")
        self.setLimits(xMin = 0, xMax = self.x_axis[-1],  yMin = self.min_signals_value, yMax = self.max_signals_value)
            # , yMin = self.min_signals_value, yMax = self.max_signals_value
        
            # print(f'{self.viewRange()} mm')
        
    def replay(self):
        if len(self.__channels):
            #add a line that reset the audio to the begining
            self.play()
            self.counter = 0
        
    def pause(self):
        self.play_state = False
        ## add a line to stop playing the audio
        self.timer.stop()
        
      
        
