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
        self.pressure_max = 70
        self.pressure_start = 40
                       # 0 - local,      1-шур_11
        self.hosts = ["localhost", "192.168.30.111", "192.168.30.121", "192.168.30.211", "192.168.30.221"]
        self.time_d = 3

        self.data_to_PLC = [self.pressure_start, self.pressure_start, self.pressure_start, self.sensor_ready,
                            self.sensor_ready, self.regim_code]

        self.data_for_gui = [self.hosts, self.time_d, self.regim_name, self.regim_code, self.ready_to_start, self.pressure_max]

    def get_data_for_gui(self):
        return self.data_for_gui
    
    def get_data_to_PLC(self):
        return self.data_to_PLC
        
    def update_data_to_PLC(self):
        self.data_to_PLC[0] = self.data_to_PLC[0] + 1
        if self.data_to_PLC[0] >= self.pressure_max:
            self.data_to_PLC[0] = 1
        self.data_to_PLC[1] = self.data_to_PLC[1] + 2
        if self.data_to_PLC[1] >= self.pressure_max:
            self.data_to_PLC[1] = 1
        self.data_to_PLC[2] = self.data_to_PLC[2] + 3
        if self.data_to_PLC[2] >= self.pressure_max:
            self.data_to_PLC[2] = 1