import time
from gui_imitator import Imitator
from gui_sarz import Sarz
from model_NV import ModelNV
from connect_to_PLC import ConnectPLC
from settings import *

def main():
    model = ModelNV()
    c = ConnectPLC()
    imi = Imitator(model, c)
    sarz = Sarz()

    while True:
        imi.start()
        sarz.update(c.mediana)
        data_plc = imi.get_data()
        sarz.start()
        c.write_to_PLC(data_plc)
        c.read_PLC()
        time.sleep(TIME_MAIN)
    # try:
    #     sys.exit(app.exec())
    # except:
    #     print("Bye!")


if __name__ == '__main__':
    main()
