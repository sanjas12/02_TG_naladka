from pyModbusTCP.client import ModbusClient 
import time

LOCAL = 'localhost'
SHUR_11 = '192.168.30.111'

try:
    c = ModbusClient(host=LOCAL, port=502)
    # c = ModbusClient(host=SHUR_11, port=502)
except ValueError:
    print("Error with host or port params")

data = [0, 0, 0, 0]

while True:
    time.sleep(1)
    w = c.write_multiple_registers(regs_addr=15, regs_value=data)
    data[0] = data[0] + 1
    if data[0] >= 99:
        data[0] = 1
    data[1] = data[1] + 2
    if data[1] >= 99:
        data[1] = 1
    data[2] = data[2] + 3
    if data[2] >= 99:
        data[2] = 1
    r = c.read_input_registers(reg_addr=15, reg_nb=len(data))
    print(r)
