import struct
import time

# prs_cur = [0, 17116]

# mypack_3 = struct.pack('<hh', *prs_cur)

# real_5 = struct.unpack('<f', mypack_3)

# print(real_5[0])


qp = [0, 0, 55296, 17896, 10240, 17856, 43008, 17857, 57672, 17015]

out = []
# in = [ ]

for _ in range(0, len(qp), 2):
    mypack_3 = struct.pack('<HH', qp[_], qp[_+1])
    real_5 = struct.unpack('<f', mypack_3)[0]
    out.append(real_5)

print(out)

print(list(map(lambda x: round(x, 2), out)))