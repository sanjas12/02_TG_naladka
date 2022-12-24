import struct
from pyModbusTCP.client import ModbusClient 
from model_NV import ModelNV
import time
import random
from settings import *
import numpy as np

class ConnectPLC():

    def __init__(self, number_cabinet):
        self.model = ModelNV()
        self.addr_start_write = 15

        # qp - param
        # 1246 - prs.aim
        # 1248 - GPK[0].cur
        # 1250 - GPK[1].cur
        # 1252 - GPK[2].cur
        # 1254 - prs.cur
        self.addr_start_read = 1246
        self.number_param_read = 5 
        self.cabinet_name = ('local host', 'шур-11', 'шур-12', 'шур-21', 'шур-22')
        self.cabinet_number = number_cabinet
                       # 0 - local,      1-шур_11       2-шур_12          3-шур_21              4-шур_22
        self.hosts = ["localhost", "192.168.30.111", "192.168.30.121", "192.168.30.211", "192.168.30.221"]
        self.prs_cur = 0
        
        try:
            self.c = ModbusClient(host=self.hosts[self.cabinet_number], port=502, timeout=TIME_TO_CONNECT)
        except ValueError:
            print("Error with host or port params")

    def get_data_to_PLC(self):
        self.model.update_data_to_PLC()
        self.data_to_PLC = self.model.get_data_to_PLC()

    def write_to_PLC(self, data):
        # print(data)
        # print(self.addr_start_write, type(data))
        # try:
        w = self.c.write_multiple_registers(regs_addr=self.addr_start_write, regs_value=data)
        print(f'to PLC ({self.cabinet_name[self.cabinet_number]}) -> {data}')           
        # except TypeError:
            # print("не запущен Unity Pro")

    def read_PLC(self):
        # PLC Premium m[1] real (занимает 2 адреса) выдает как WORD (2 int) -> python принимает как list[2 int]  
            # PLC(115.0) -> Python ([0, 17126])  
            # PLC(110.0) -> Python ([0, 17116])  
                                                                                         # *2 - потомучто real занимает два  адреса)
        qp_param = self.c.read_input_registers(reg_addr=self.addr_start_read, reg_nb=self.number_param_read * 2) 

        self.out = []
        try:
            for _ in range(0, len(qp_param), 2):
                mypack_3 = struct.pack('<HH', qp_param[_], qp_param[_+1])
                real_5 = struct.unpack('<f', mypack_3)[0]
                self.out.append(real_5)
            print('qp param <-',list(map(lambda x: round(x, 2), self.out)))
        except:
            print('Нет соединения с UNity 7')
        return self.out

    @property
    def mediana(self):
        return round(self.out[4], 2)

def main():
    c = ConnectPLC(1)
    c1 = ConnectPLC(3)
    start = 6000
    target = 4700
    end = 8000
    data = [0 for _ in range(44)]
    data1 = [0 for _ in range(44)]
    while True:
        # data = [random.randint(start, end) for _ in range(44)]
        data[0], data[1], data[2] = [target for _ in range(3)]
        data[43] += 2   # счетчик для NSI
        data[6] = 1   # СК открыты\закрыты
        if data[43] > 32000:
            data[43] = 1
    
        data1[0], data1[1], data1[2] = [target for _ in range(3)]
        data1[43] += 2   # счетчик для NSI
        data1[6] = 1   # СК открыты\закрыты
        if data1[43] > 32000:
            data1[43] = 1
    
    
        c.write_to_PLC(data)
        c1.write_to_PLC(data)
        # c.read_PLC()
        try:
            print(c.mediana)
        except:
            print("Нет соединения c Unity")
        time.sleep(TIME_TO_CONNECT)

if __name__ == '__main__':
    main()