import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import numpy as np
from math import inf

import sounddevice as sd

from classes.CustomSignal import CustomSignal



class Viewer(pg.PlotWidget):
    def __init__(self, id:int = 1):
        super().__init__()
        self.label = None
        self._current_signal = None
        self.id = id
        self.window_size = 0.05 # [0:100] a normalized value that decide what % of the signal will be viewed on the screen

        self.__rewind_state = False
        self.__cine_speed = 70 # 
        self.signal_update_speed = 10
        self.signal_update_speed_iterartion = 1

        self.speed_iteration = 10
        self.__zoom = 1
        
        self.x_axis = []
    
        self.drag_active = False  
        
        self.play_state = False
        
        self.viewBox = self.getViewBox()
        self.time_window = 1000
        self.sampling_rate = 1  # Default value to avoid division errors if unset
        self.total_duration = 1  # Will be updated when adding a channel        
        self.max_signals_value = -inf
        self.min_signals_value = inf    
        
        # self.scrolling_in_y_axis = False
        
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_signal)



            
    def update_signal(self):
        """Update the visible range based on the counter while limiting x-axis within bounds."""           
        # Calculate the range to display, constrained by the x-axis boundaries
        # speed controls need to be modifed to adjust based on the signal it self and ists window
        start_value = max(0, self.viewRange()[0][0])+((self.signal_update_speed)/100)*self.window_size*self.x_axis[-1]
        end_value = min(start_value + self.window_size*self.x_axis[-1], self.x_axis[-1])
        
        start_idx = int(start_value*self.sampling_rate)
        end_idx = int(end_value*self.sampling_rate)
        
        self.setLimits(yMin=int(min(self.y_axis[start_idx:end_idx])) , yMax=int(max(self.y_axis[start_idx:end_idx])))
        
        if end_value >= self.x_axis[-1]:
            self.timer.stop()
        # Update the visible range on the plot
        self.setXRange(start_value, end_value)
        
            
        # print(self)
    
   
    def add_signal(self , signal:CustomSignal):
        if isinstance(signal, CustomSignal):
            if not np.isfinite(signal.original_signal[1]).all() or len(signal.original_signal[1]) == 0:
                print("Channel signal contains invalid data (inf/nan or empty).")
                return
            
            self.x_axis = []
            self.y_axis = []
            
            self.x_axis = signal.original_signal[0] # x values based on the signal length
            self.sampling_rate = signal.signal_sampling_rate
            
            if self.id == 1:
                self.label = 'Original'
                self.y_axis = signal.original_signal[1]
            elif self.id == 2:
                self.label = 'Modified'
                self.y_axis = signal.reconstructed_signal[1]
            # print(f'x type: {type(self.x_axis)} x length: {len(self.x_axis)} y type:{type(self.y)}')
            self.plot(self.x_axis, self.y_axis, pen=pg.mkPen(color='r'))
            
            self.setLimits(xMin=0,xMax=self.x_axis[-1],yMin=int(min(self.y_axis)), yMax=int(max(self.y_axis)))
            
        else:
            raise Exception("The new channel must be of class Channel")
            
    
    def play(self):
        """Starts or resumes the timer, ensuring it uses the updated counter value."""
        if self.play_state:
            self.play_state = False
            self.timer.stop()  # Ensure the timer is fully reset
        else: 
            self.play_state = True
            self.timer.start(int(self.__cine_speed))

        
    def replay(self):
        start_value = 0
        end_value = self.window_size*self.x_axis[-1]
        self.setXRange(start_value, end_value)        
    
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
    def cine_speed_up(self):
        if(self.__cine_speed <=100 and self.signal_update_speed <15):
            self.__cine_speed += self.speed_iteration
            self.signal_update_speed += self.signal_update_speed_iterartion
        else:
            raise Exception("Speed of cine must be less than 100")
        pass
    def cine_slow_down(self):
        if(self.__cine_speed > 49 and self.signal_update_speed > 5):
            self.__cine_speed -= self.speed_iteration
            self.signal_update_speed -= self.signal_update_speed_iterartion

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

