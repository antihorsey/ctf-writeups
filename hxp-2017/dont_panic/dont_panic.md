Don't Panic
===

Don't Panic was another large, statically-compiled, stripped binary, except
this one was written in Go to add a new wrinkle.

Looking at the ELF we see two sections specific to Go: `.gosymtab` and
`.gopclntab`. The first is supposed to contain symbols but unfortunately is
empty. The second contains PC to line number mappings, which might have been
of some use but probably not much. I couldn't quickly find anything that
detailed how the section was laid out or any utilties to work with it other
than the gosym module which didn't seem to have a very useful interface for
this purpose. I didn't waste too much time because the mapping seemed like it
would be of limited use.

So I took a different tack of searching for the "Nope." string that was printed
when the wrong flag was provided. I got lucky and found a function that
referenced both that string and another string "Seems like you got a flag..."
so I knew I was in the right place.

After manually reversing for a while I learned there were two tables. The
second table was used to generate a value from each flag character: the
flag character was used as an index into the table. That table entry was then
used as the next index which chose another entry in the table and so on and so
forth until it found the 0xFF entry. Each time it performed a lookup it
incremented a counter. The final counter value was then compared against a
value from the second table. If the values matched it proceeded to the next
character from the provided flag, else it printed the "Nope." message and
exited.

I extracted the first table and wrote a Python script to generate a reverse
mapping that could be used to map entries in the second table directly to the
character needed in the flag. After making sure it worked for the first
character to produce 'h' (from 'hxp{') I quickly discovered that the first
table changed for each subsequent character of the flag.

Rather than copying out each table for each character of the flag, I decided
it was time for another approach. The icount example from Pin had worked well
on Revenge of the Zwiebel so I decided to see if I could try something similar.
I knew the total number of instructions wasn't going to work for this binary
because of the way the table lookup worked -- the highest number of
instructions would just pick the character that incremented the counter the
most times instead of pciking the character that incremented it the right
number of times.

But I could see the branch where it was doing the comparison and found the
RIP value when the check succeeded, so I made a small modification to the
icount example to only increment the instruction counter when RIP was equal
to the value of the success branch. I tried it with the first few characters
that I knew were in the flag and it worked well: "xyzzzzzzzzzzzzzzzz..."
returned 0 whereas "hxp{xxxxxxxxxxxxxxx...." returned 4. (There was also a
check before it even got to this section that the total number of characters
in the flag was at least 40 or so.)

I re-used most of the script from Revenge of the Zwiebel but using a different
version I had tried that guessed each character one at a time. It took a while
to execute the binary each time since I was in effect adding a conditional
branch to each and every instruction executed. But the script to bruteforce it
still ran in a reasonable amount of time (about 10 minutes) and finally
finished when it finally provided the correct flag and the binary itself
printed a message to stderr, causing my script to fail parsing the Pin output
and die with an error. But I had the flag and that's all I needed:

    hxp{k3eP_C4lM_AnD_D0n't_P4n1c__G0_i5_S4F3}

(Unfortunately I don't still have the source for the modified Pin example that
I used to build my_count.so. But the changes were minimal, just a couple of 
small additions to pass the current RIP value to the docount function and then
check it against the desired value.)

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
