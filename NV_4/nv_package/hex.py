import struct
import time

prs_cur = [0, 17116]

mypack_3 = struct.pack('<hh', *prs_cur)

real_5 = struct.unpack('<f', mypack_3)

print(real_5[0])