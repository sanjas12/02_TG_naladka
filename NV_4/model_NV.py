from pyModbusTCP.client import ModbusClient 
import time



class ModelNV():

    def __init__(self):
        self.hosts = ["localhost", "192.168.30.111", "192.168.30.121", "192.168.30.211", "192.168.30.221"]
        self.time_d = 3
        self.regim_name = """
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
        self.regim = [9,10, 11, 12, 14, 15, 16, 17, 20, 21, 22, 23, 24, 29]
        self.ready = 0
        self.pressure_max = 70
        self.data_for_gui = [self.hosts, self.time_d, self.regim_name, self.regim, self.ready, self.pressure_max]


        try:
                                #  0 - local, 1-шур_11
            self.c = ModbusClient(host=self.hosts[0], port=502)
        except ValueError:
            print("Error with host or port params")

        # 0 - 1 Датчик ГПК                              -> M[15]
        # 1 - 2 Датчик ГПК                              -> M[16]
        # 2 - 3 Датчик ГПК                              -> M[17]
        # 3 - Исправность датчиков ГПК (0 - исправны)   -> M[18]

        # 4 - готовность к пуску (1 - готов)            -> M[19]
        # 5 - Переход в режим (10 - default)            -> M[20]
        self.data = [0, 0, 0, 0,
                self.ready, self.regim[1]]

    def set_data(self):
        w = self.c.write_multiple_registers(regs_addr=15, regs_value=self.data)
        self.data[0] = self.data[0] + 1
        if self.data[0] >= self.pressure_max:
            self.data[0] = 1
        self.data[1] = self.data[1] + 2
        if self.data[1] >= self.pressure_max:
            self.data[1] = 1
        self.data[2] = self.data[2] + 3
        if self.data[2] >= self.pressure_max:
            self.data[2] = 1
        r = self.c.read_input_registers(reg_addr=15, reg_nb=len(self.data))
        print(r)
        time.sleep(self.time_d)
