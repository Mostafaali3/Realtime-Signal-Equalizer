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
    def __init__(self, file_path = '', wave_type = 'audio', mono = True, sampling_rate = None, data = None):
        if wave_type == 'uniform':
            pass
        if wave_type == 'audio':
            if data == None:
                self.y_array, self.sampling_rate = librosa.load('D:/SBME/DSP/Tasks/DSP-Signal-Equalizer/data/test.mp3', sr=sampling_rate, mono=mono)
                self.duration = len(self.y_array) / self.sampling_rate
                self.x_array = np.linspace(0, self.duration, len(self.y_array))
            else:
                self.y_array = data # handle the case when the wave is composed in the program
        pass
    
    def len(self):
        return len(self.y_array)
        

class Channel(Waveform):
    def __init__(self,  color = "r", label = "signal", visability=True):
        super().__init__()
        self.__color = color
        self.__label = label
        self.__signal = self.y_array
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
        self.__signal = value

        
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
        self.__channel = None
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
        

        if self.counter + self.time_window > len(self.channel):
            self.timer.stop()
        min_channel_interval_value = min(self.channel.signal[self.counter:self.counter + self.time_window])
        # if min_channel_interval_value < min_interval_value:
        #     min_interval_value = min_channel_interval_value
        max_channel_interval_value = max(self.channel.signal[self.counter:self.counter + self.time_window])
        # if max_channel_interval_value > max_interval_value:
        #     max_interval_value = max_channel_interval_value

    def add_channel(self , new_channel):
        if isinstance(new_channel, Channel):
            if not np.isfinite(new_channel.signal).all() or len(new_channel.signal) == 0:
                print("Channel signal contains invalid data (inf/nan or empty).")
                return
            if len(new_channel) == 0:
                raise Exception("Channel signal data is empty")
            
            self.__channel = new_channel
            self.x_axis = new_channel.x_array # x values based on the signal length
            self.plot(new_channel.x_array, new_channel.signal, pen=pg.mkPen(color=new_channel.color))

            # Play automatically if data is valid
            self.play()
        else:
            raise Exception("The new channel must be of class Channel")
            
    # def play(self):
    #     if self.play_state == False:
    #         self.play_state = True
    #         self.timer.start(self.__cine_speed)
    #         # print(self.__cine_speed)
    #     if self.y_axis_scroll_bar_enabled:
    #         self.viewBox.setMouseEnabled(x = True, y =True)
            
    #         self.viewBox.enableAutoRange(x=False, y=False)
    #         self.viewBox.setAutoVisible(x=False, y=False)
    #     else:
    #         self.viewBox.setMouseEnabled(x = True, y =False)
    #         self.viewBox.enableAutoRange(x=False, y=True)
    #         self.viewBox.setAutoVisible(x=False, y=True)
    #         # self.setYRange(self.viewRange()[1][0], self.viewRange()[1][1])
    #     print(self.viewRange())
    #     self.setXRange(self.viewRange()[0][0]+50, self.viewRange()[0][0]+1000)
    #     self.counter = int(max(0,self.viewRange()[0][0]))
    #         # print(f"{self.counter} this is counter from the play")
    #     self.setLimits(xMin = 0, xMax = self.x_axis[-1],  yMin = self.min_signals_value, yMax = self.max_signals_value)
    #         # , yMin = self.min_signals_value, yMax = self.max_signals_value
        
    #     # print(f'{self.viewRange()} mm')
    def play(self):
        if not self.play_state and self.__channel is not None:
            if len(self.x_axis) > 0 and len(self.__channel.signal) > 0:
                self.play_state = True
                self.timer.start(self.__cine_speed)
                self.counter = int(max(0, self.viewRange()[0][0]))
                # Set X and Y ranges only if finite values are available
                x_min, x_max = np.min(self.x_axis), np.max(self.x_axis)
                y_min, y_max = np.min(self.__channel.signal), np.max(self.__channel.signal)
                if np.isfinite([x_min, x_max, y_min, y_max]).all():
                    self.setLimits(xMin=x_min, xMax=x_max, yMin=y_min, yMax=y_max)
                    self.setXRange(self.viewRange()[0][0] + 50, self.viewRange()[0][0] + 1000)
                else:
                    print("Signal data has invalid range limits (inf/nan).")
            else:
                print("Cannot play: x_axis or channel signal is empty.")
        
    def replay(self):
        if len(self.__channels):
            self.play()
            self.counter = 0
        
    def pause(self):
        self.play_state = False
        self.timer.stop()
        
    
    def rewind(self):
        self.__linked_rewind_state = not self.__linked_rewind_state
        pass    
    
    def zoom_in(self):
        pass
    
    def zoom_out(self):
        pass
    
    def update_x_axis(self):
        self.x_axis = list(range(max(self.__channel.signal)))
    
        
    @property
    def cine_speed(self):
        return self.__cine_speed
    
    # @cine_speed.setter
    def cine_speed(self , new_speed):
        """
        new_speed: the input must range between 10 and 50 
        """
        if(new_speed > 0):
            self.__cine_speed = new_speed
            # self.pause()
            # self.play()
        else: 
            raise Exception("Speed of cine must be greater than zero")
        pass
    
    @property
    def rewind_state(self):
        return self.__rewind_state
    
    @rewind_state.setter
    def rewind_state(self, new_rewind_state):
        self.__rewind_state = new_rewind_state
    
    @property
    def channel(self):
        return self.__channel
    
    @property
    def zoom(self):
        return self.__zoom
    
    @zoom.setter
    def zoom(self , new_zoom):
        if(new_zoom > 0 ):
            self.__zoom = new_zoom
        else:
            raise Exception("Value of zoom must be greater than zero")
        
    def drag_and_move(self):
        self.drag_active = True
        print("draging")
        # super().dragMoveEvent(event)  # Call the base class implementation if needed
    
    def reset_drag_flag(self):
        """Reset drag flag to False after the event."""
        self.drag_active = False

def test_waveform_viewer():
    # Initialize QApplication
    app = QApplication(sys.argv)
    
    # Set up a test file path (replace this with an actual audio file path)
    file_path = "path/to/your/test_audio.mp3"  # Replace with a valid path to an audio file
    
    # Create a Waveform instance
    try:
        waveform = Waveform(file_path=file_path, wave_type='audio', mono=True)
    except Exception as e:
        print(f"Error loading waveform: {e}")
        return

    # Create a Channel instance, passing waveform's data and configuring other properties
    channel = Channel(color="b", label="Test Signal")
    channel.signal = waveform.y_array  # Assign waveform data to the channel signal
    
    # Set up the Viewer
    viewer = Viewer()
    viewer.add_channel(channel)  # Add the channel to the viewer
    
    # Configure main window
    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    layout.addWidget(viewer)
    window.setCentralWidget(central_widget)
    window.setWindowTitle("Audio Waveform Viewer")
    window.resize(800, 600)
    window.show()
    
    # Start the QApplication loop
    sys.exit(app.exec_())

# Run the test function
if __name__ == "__main__":
    test_waveform_viewer()