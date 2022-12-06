import struct


prs_cur = [0, 17116]

print(hex(prs_cur[0]))
print(hex(prs_cur[1]))

mypack = struct.pack('<ii', prs_cur[0], prs_cur[1])


print(mypack)
print(hex(mypack))