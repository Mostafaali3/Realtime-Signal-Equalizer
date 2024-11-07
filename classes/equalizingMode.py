from classes import CustomSignal


class EqualizingMode():
    def __init__(self, current_signal:CustomSignal = []):
        self.current_signal = current_signal
        
    def transform(self, signal:CustomSignal):
        '''
        this function is to make the frequency transform on the data given 
        '''
        pass
    
    def inverse(self, signal:CustomSignal):
        '''
        this function is to restor the signal from its frequencies including the shift
        '''
        pass
    
    def equalize(self, data_x, data_y, factor):
        '''
        this function is to amplify or reducing the amplitude if the data in a specific given region
        '''
        pass 