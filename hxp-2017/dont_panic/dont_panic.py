#!/usr/bin/env python3

import multiprocessing, os, random, string, subprocess, time

CHARSET = (string.ascii_letters + string.digits + string.punctuation).encode('ascii')
#CHARSET = list(range(128))

TOP_SIZE = 20
START = b'A' * 0x30

def get_icount(data):
    proc = subprocess.Popen(
        args=['/tmp/pin-3.5/pin','-t','my_count.so','--','./main_strip',data],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = proc.communicate(b'')

    # Count 43444
    stderr = stderr.decode('ascii')
    stderr = stderr.strip()
    
    words = stderr.split()
    if len(words) < 2:
        print('what? stderr={}'.format(stderr))
        return (data,0)

    return (data,int(stderr.split()[1]))

def bruteforce():
    data, max_count = get_icount(START)

    with multiprocessing.Pool() as pool:
        for i in range(len(data)):
            datas = []
            for c in CHARSET:
                datas.append(data[:i] + bytes([c]) + data[i+1:])

            results = pool.map(get_icount, datas)
            for next_data, count in results:
                if count > max_count:
                    max_count = count
                    data = next_data
                    print('new best: {} -> {}'.format(data, max_count))
                    break

bruteforce()
