import time
import random


class data_base():
    def __init__(self):
        self.state = False
        self.data = []

    def guardar(self, data):
        if self.state == True:
            self.data.append(time.asctime(), random.randint(0, 100))
        print(self.data)

    def start(self):
        self.state = True
        print('starting')

    def stop(self):
        self.state = False
        print('stopping')



