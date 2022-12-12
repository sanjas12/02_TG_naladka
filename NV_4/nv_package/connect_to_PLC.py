import struct
from pyModbusTCP.client import ModbusClient 
from model_NV import ModelNV
import time
import random

class ConnectPLC():

    def __init__(self):
        self.model = ModelNV()
        self.addr_start_write = 15
        self.addr_start_read = 818
                       # 0 - local,      1-шур_11
        self.hosts = ["localhost", "192.168.30.111", "192.168.30.121", "192.168.30.211", "192.168.30.221"]
        self.prs_cur = 0
        
        try:
            self.c = ModbusClient(host=self.hosts[0], port=502)
        except ValueError:
            print("Error with host or port params")

    def get_data_to_PLC(self):
        self.model.update_data_to_PLC()
        self.data_to_PLC = self.model.get_data_to_PLC()

    def write_to_PLC(self, data):
        if len(data) > 5:
            # 3 датчика и испавность их
            data = data[:4]

        try:
            w = self.c.write_multiple_registers(regs_addr=self.addr_start_write, regs_value=data)
            print(data, 'to PLC')           
        except TypeError:
            print("не запущен Unity Pro")

    def read_PLC(self):
        # PLC Premium m[1] real (занимает 2 адреса) выдает как WORD (2 int) -> python принимает как list[2 int]  
            # PLC(115.0) -> Python ([0, 17126])  
            # PLC(110.0) -> Python ([0, 17116])  
        prs_cur_from_PLC = self.c.read_input_registers(reg_addr=self.addr_start_read, reg_nb=2)

        try:
            mypack_3 = struct.pack('<hh', *prs_cur_from_PLC)
            self.prs_cur = struct.unpack('<f', mypack_3)[0]
            print(round(self.prs_cur, 2), 'кг\см3', 'From PLC')
        except:
            pass
        return self.prs_cur

def main():
    c = ConnectPLC()
    start = 6000
    end = 8000
    while True:
        data = [random.randint(start, end), random.randint(start, end), random.randint(start, end)]
        c.write_to_PLC(data)
        c.read_PLC()
        time.sleep(1)

if __name__ == '__main__':
    main()