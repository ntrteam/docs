#!/usr/bin/python3

import struct
import sys

with open(sys.argv[1], 'rb') as f:
    fdata = f.read()

# ff = b'\xFF'*0x1000
zz = b'\x00'*0x1000
maps = struct.unpack("<8192H", fdata[0:0x4000])
with open(sys.argv[2], 'wb') as f:
    for i in range(32*1024*1024//0x1000):
        if maps[i%8192] == 0xFFFF:
            f.write(zz) #fdata[0x10000:0x10200]*8)
            continue
        offs = maps[i%8192]*0x1000
        f.write(fdata[offs:offs+0x1000])
    