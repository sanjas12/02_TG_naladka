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
        
    def connect(self):
        try:
            self.c = ModbusClient(host=self.hosts[0], port=502)
        except ValueError:
            print("Error with host or port params")

    def get_data_to_PLC(self):
        self.model.update_data_to_PLC()
        self.data_to_PLC = self.model.get_data_to_PLC()

    def data_transfer(self, data):
        self.connect()
        # self.get_data_to_PLC()
        if len(data) > 5:
            # 3 датчика и испавность их
            data = data[:4]
        print(data, 'to PLC')           
        w = self.c.write_multiple_registers(regs_addr=self.addr_start_write, regs_value=data)
        time.sleep(1)
        # PLC Premium m[1] real (занимает 2 адреса) выдает как WORD (2 int) -> python принимает как list[2 int]  
        prs_cur = self.c.read_input_registers(reg_addr=self.addr_start_read, reg_nb=2)
        # prs_cur = bin(prs_cur[0])+ bin(prs_cur[1])
        
        # PLC(115.0) -> Python ([0, 17126])  
        # PLC(110.0) -> Python ([0, 17116])  


        # Convert 2 ints to float
        print(hex(prs_cur[0]))
        print(hex(prs_cur[1]))

        mypack = struct.pack('>ii', prs_cur[0], prs_cur[1])
        print (mypack)
        
        mypack = struct.pack('<ii', prs_cur[0], prs_cur[1])
        print (mypack)

        # print(struct.unpack('<f', mypack))
        # print(struct.unpack('>f', mypack))










        # high_word = bytearray(prs_cur[0])
        # high_word.reverse()
        # print(high_word)
        # low_word = bytearray(prs_cur[1])
        # low_word.reverse()
        # prs_cur = struct.unpack('f', low_word+high_word)
        
        # print(prs_cur, type(prs_cur), 'кг\см3')
        # print(bin(prs_cur)<<8, 'кг\см3')
        print(type(prs_cur), prs_cur, 'кг\см3')

    def get_data(self):
        return self.data_to_PLC


def main():
    c = ConnectPLC()
    start = 6000
    end = 8000
    while True:
        data = [random.randint(start, end), random.randint(start, end), random.randint(start, end)]
        # data = [11000, 11000, 11000]
        c.data_transfer(data)



if __name__ == '__main__':
    main()