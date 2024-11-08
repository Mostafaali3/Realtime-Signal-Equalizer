from classes import CustomSignal

class controller():
    '''
    mode: should be one of 
    '''
    def __init__(self, signal:CustomSignal, mode:str):
        self.current_signal = signal