import time
from settings import *


class ModelNV():

    def __init__(self):
        self.all_regim_name =   """
                                9 - Технолог
                                10 - Останов
                                11 - Исходное
                                12 - Опроб 1
                                14 - РЧВ
                                15 - Опроб
                                16 - РСН1
                                17 - Синхр
                                20 - РПК 
                                21 - РМ
                                22 - РС
                                23 - РДС
                                24 - РД-2
                                29 - ОПРЧ 
                                """
        self.regim_name = ['Технолог','Останов','Исходное','Опроб 1','РЧВ','Опроб','РСН1','Синхр',
                            'РПК', 'РМ', 'РС', 'ОПРЧ']
        self.regim_code = [9, 10, 11, 12, 14, 15, 16, 17, 20, 21, 22, 23, 24, 29]
        self.sensor_ready = 0
        self.ready_to_start = 1
        self.pressure_start = 4000
        self.pressure_max = 7000
        self.pressure_target = 6000
                       # 0 - local,      1-шур_11
        self.hosts = ["localhost", "192.168.30.111", "192.168.30.121", "192.168.30.211", "192.168.30.221"]
        self.time_d = 3
        
        # 0 - 1 Датчик ГПК                              -> M[15]
        # 1 - 2 Датчик ГПК                              -> M[16]
        # 2 - 3 Датчик ГПК                              -> M[17]
        # 3 - Исправность датчиков ГПК (0 - исправны)   -> M[18]
        
        # 4 - готовность к пуску (1 - готов)            -> M[19]
        # 5 - Переход в режим (10 - default)  
        # 6 - заданное давление  

        self.data_to_PLC = [0 for _ in range(30)]

        print(len(self.data_to_PLC))

        self.data_to_PLC = [self.pressure_start, self.pressure_start, self.pressure_start, self.sensor_ready,
                            self.sensor_ready, self.regim_code, self.pressure_target]

        self.data_for_gui = [self.hosts, self.time_d, self.regim_name, self.regim_code, 
                            self.ready_to_start, self.pressure_max]

    def get_data_for_gui(self):
        return self.data_for_gui
    
    def get_data_to_PLC(self):
        self.update_data_to_PLC()
        return self.data_to_PLC
        
    def update_data_to_PLC(self):
        self.data_to_PLC[0] = self.data_to_PLC[0] + 100
        if self.data_to_PLC[0] >= self.pressure_max:
            self.data_to_PLC[0] = self.pressure_start
        self.data_to_PLC[1] = self.data_to_PLC[1] + 200
        if self.data_to_PLC[1] >= self.pressure_max:
            self.data_to_PLC[1] = self.pressure_start
        self.data_to_PLC[2] = self.data_to_PLC[2] + 300
        if self.data_to_PLC[2] >= self.pressure_max:
            self.data_to_PLC[2] = self.pressure_start


def main():
    model = ModelNV()
    while True:
        # model.get_data_to_PLC()
        print(model.get_data_to_PLC())
        time.sleep(1)

if __name__ == '__main__':
    main()
