from pyModbusTCP.client import ModbusClient 
from model_NV import ModelNV
import time

class ConnectPLC():

    def __init__(self):

        self.model = ModelNV()

        
        self.start_addr = 15
        
    
    
    def connect(self):
        try:
            self.c = ModbusClient(host=self.hosts[0], port=502)
        except ValueError:
            print("Error with host or port params")

    def get_data_to_PLC(self):
        self.model.update_data_to_PLC()
        self.data_to_PLC = self.model.get_data_to_PLC()

    def data_transfer(self):
        self.get_data_to_PLC()
        # w = self.c.write_multiple_registers(regs_addr=self.start_addr, regs_value=self.data_to_PLC)
        time.sleep(1)
        print(self.data_to_PLC)
        # r = self.c.read_input_registers(reg_addr=self.start_addr, reg_nb=len(self.data_to_PLC))

    def get_data(self):
        return self.data_to_PLC


def main():
    c = ConnectPLC()
    while True:
        c.data_transfer()



if __name__ == '__main__':
    main()