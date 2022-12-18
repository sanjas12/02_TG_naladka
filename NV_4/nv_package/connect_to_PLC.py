import struct
from pyModbusTCP.client import ModbusClient 
from model_NV import ModelNV
import time
import random
from settings import *

class ConnectPLC():

    def __init__(self):
        self.model = ModelNV()
        self.addr_start_write = 15
        
        # 1246 - prs.aim
        # 1248 - GPK[0].cur
        # 1250 - GPK[1].cur
        # 1252 - GPK[2].cur
        # 1254 - prs.cur
        self.addr_start_read = 1246
        self.number_param = 5 
                       # 0 - local,      1-шур_11
        self.hosts = ["localhost", "192.168.30.111", "192.168.30.121", "192.168.30.211", "192.168.30.221"]
        self.prs_cur = 0
        
        try:
            self.c = ModbusClient(host=self.hosts[0], port=502, timeout=TIME_TO_CONNECT)
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
            # print('to PLC',  time.asctime(), data, )           
            print('to PLC ->', data)           
        except TypeError:
            print("не запущен Unity Pro")

    def read_PLC(self):
        # PLC Premium m[1] real (занимает 2 адреса) выдает как WORD (2 int) -> python принимает как list[2 int]  
            # PLC(115.0) -> Python ([0, 17126])  
            # PLC(110.0) -> Python ([0, 17116])  
                                                                                         # *2 - потомучто real занимает два  адреса)
        qp_param = self.c.read_input_registers(reg_addr=self.addr_start_read, reg_nb=self.number_param * 2) 

        # print("qp_param", qp_param, len(qp_param))

        self.out = []
        try:
            for _ in range(0, len(qp_param), 2):
                # mypack_3 = struct.pack('<hh', qp_param[_], qp_param[_+1])
                mypack_3 = struct.pack('<HH', qp_param[_], qp_param[_+1])
                real_5 = struct.unpack('<f', mypack_3)[0]
                self.out.append(real_5)
                # print(round(self.prs_cur, 2), 'кг\см3', 'From PLC')
            print('qp param <-',list(map(lambda x: round(x, 2), self.out)))
        except:
            print('Нет соединения с UNity 7')
        return self.out

    @property
    def mediana(self):
        return round(self.out[4], 2)

def main():
    c = ConnectPLC()
    start = 6000
    end = 8000
    while True:
        data = [random.randint(start, end), random.randint(start, end), random.randint(start, end)]
        c.write_to_PLC(data)
        c.read_PLC()
        print(c.mediana)
        time.sleep(TIME_TO_CONNECT)

if __name__ == '__main__':
    main()