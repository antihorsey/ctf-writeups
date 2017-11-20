#!/usr/bin/env python3

import binascii, struct, zlib, json

def xor(a,b):
    assert len(a) == len(b)
    return bytes([a[i] ^ b[i] for i in range(len(a))])

def tamper(hex_cipher):
    '''
        >>> tamper('256248bf08062fd9d60de4bd93602604174747cdc78ce02882bc580ebc59de14')
        256248bf08062fd9d60de5bd93602604174747cdc78ce02882bc580e5def8cfb
    '''
    cipher = binascii.unhexlify(hex_cipher)

    C = cipher[:-4]
    C_crc, = struct.unpack('<L', cipher[-4:])

    zero = b'\x00' * len(C)

    pos = 10
    X = zero[:pos] + b'\x01' + zero[pos+1:]

    C_prime = xor(C, X)

    crc_X = zlib.crc32(X)
    crc_0 = zlib.crc32(zero)
    C_crc_prime = C_crc ^ crc_X ^ crc_0

    new_cipher = C_prime + struct.pack('<L', C_crc_prime)
    return binascii.hexlify(new_cipher).decode()

print(tamper(input().strip()))
