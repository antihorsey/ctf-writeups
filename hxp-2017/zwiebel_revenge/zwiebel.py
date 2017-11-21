#!/usr/bin/env python3

import multiprocessing, os, random, string, subprocess, time

#CHARSET = (string.ascii_letters + string.digits + string.punctuation).encode('ascii')
CHARSET = list(range(256))

TOP_SIZE = 20
START = b'A' * 0x90

def get_icount(data):
    proc = subprocess.Popen(
        args=['/tmp/pin-3.5/pin','-t','icount.so','--','./zwiebel'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = proc.communicate(data)

    # Count 43444
    stderr = stderr.decode('ascii')
    stderr = stderr.strip()
    
    words = stderr.split()
    if len(words) < 2:
        print('what? stderr={}'.format(stderr))
        return (data, 0)

    return (data, int(stderr.split()[1]))

def bruteforce():
    result = get_icount(START)
    top_results = [result]
    max_count = top_results[0][1]

    num_execs = 0
    t0 = time.time()
    update = time.time()

    with multiprocessing.Pool() as pool:
        while True:
            datas = []

            for i in range(os.cpu_count()):
                data, _ = random.choice(top_results)
                next_chars = list(data)

                num_rounds = random.randrange(1, 20)

                if random.random() < 0.5:
                    for i in range(num_rounds):
                        char = random.choice(CHARSET)
                        ndx = random.randrange(0, len(next_chars))
                        next_chars[ndx] = char
                else:
                    for i in range(num_rounds):
                        bit = 1 << random.randrange(8)
                        ndx = random.randrange(0, len(next_chars))
                        next_chars[ndx] ^= bit

                datas.append(bytes(next_chars))

            top_results += pool.map(get_icount, datas, chunksize=1)
            top_results.sort(key = lambda r: -r[1])
            top_results = top_results[:TOP_SIZE]

            if top_results[0][1] > max_count:
                max_count = top_results[0][1]
                print('new best: {} -> {}'.format(*top_results[0]))

            num_execs += len(datas)
            if time.time() - update > 10:
                update = time.time()
                print('{} execs per second'.format(num_execs / (time.time() - t0)))

bruteforce()
