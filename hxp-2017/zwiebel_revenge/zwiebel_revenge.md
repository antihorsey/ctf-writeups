Revenge of the Zwiebel
===

Revenge of the Zwiebel is a binary that asks for a flag and then checks if it's
correct. It has several anti-debugging techniques: an initializer function that
checks to make sure it can ptrace itself, and then the main flag-checking
function continually runs a few instructions and then self-modifies the next
chunk of code after each check succeeds. The amount of code that checks the
flag is fairly large, multiple kilobytes' worth, so manual analysis was out of
the question.

I tried a couple of different approaches that didn't work too well. AFL was
pretty quick to setup but didn't seem to work to well in QEMU mode with the
self-modifying code. I also started angr with a script from writeups from
zwiebel from last year, but unfortuantely I'm not that familiar with it and
I suspected there would be some twist this year that would make the solution
from last year not work.

My teammate @finalbit suggested Pin and noted that it came with an example
script to count the number of instructions. It seemed to work pretty well
so I proceeded to write a quick script to continually mutate inputs, use
Pin to count the number of instructions executed, then keep the inputs that
executed the most instructions, similar to a genetic algorithm but without
any recombination.

After a while, the broad outline of a flag started to emerge:

    `new best: b'ipp{1_5m1l\xe4_l4zync\x15q}`

Over time, more and more lowercase letters and digits popped out and
the initial htp{ changed to hxp{. And finally it got fairly close:

    `new best: b'ixp{1_5m3ld_l4zync55}`

which was close enough to guess the correct flag: `hxp{1_5m3ll_l4zyn355}`

The following script took about 30 minutes to run. The final number of
instructions executed for a correct flag is 133827771 if you want to judge
its progress.

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
