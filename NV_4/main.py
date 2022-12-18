import time
from nv_package.gui_imitator import Imitator
from nv_package.gui_sarz import Sarz
from nv_package.model_NV import ModelNV
from nv_package.connect_to_PLC import ConnectPLC
from nv_package.settings import *

def main():
    model = ModelNV()
    c = ConnectPLC()
    imi = Imitator(model, c)
    sarz = Sarz(model)

    while True:
        imi.start()
        sarz.update_data()
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
