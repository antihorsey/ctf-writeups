Problem statement:

> The hacker Th3 Pr0f3ss0r figured out a new way to use RSA encryption to send
flags to his CTF group.

> Will you be able to decipher the message and retrieve the flag?

And then two files were attached:

[flag.enc](flag.enc)

[pub.key](pub.key)

Well, first things first. Let's look at pub.key first since flag.enc likely
won't be very useful.

```sh
$ openssl rsa -in pub.key -pubin -noout -text
Public-Key: (1683 bit)
Modulus:
    04:13:cf:27:35:04:00:75:00:68:00:05:5b:0e:c2:
    19:83:8d:e2:3c:00:00:01:86:00:00:00:68:00:00:
    03:93:80:f2:3d:5b:ea:1d:ed:1b:15:db:a0:47:76:
    35:45:dc:fc:75:e9:4c:71:d7:81:fd:b0:bb:b6:53:
    7a:2f:41:88:1e:89:8d:3d:e7:df:50:3d:37:28:a8:
    45:e9:df:6d:7c:60:36:68:13:cf:5b:68:19:83:8d:
    e2:3c:00:00:01:86:00:00:04:13:cf:0d:1b:93:01:
    04:00:75:00:68:00:05:5b:0e:c2:19:83:8d:e2:3c:
    00:00:01:86:00:00:00:68:01:d4:00:00:00:00:00:
    00:01:a0:00:00:00:00:00:00:03:93:80:f2:3d:5b:
    ea:1d:e4:82:01:a0:00:00:00:00:00:0d:01:38:00:
    b6:85:6f:6d:2b:51:aa:0d:02:71:6e:94:3d:44:aa:
    0f:53:c0:50:39:75:51:aa:11:13:cf:41:4e:00:00:
    00:00:0d:00:0d:04:92:00:00:04:fa:00:00:00:df:
    e5
Exponent: 65537 (0x10001)
```

The exponent looks normal at least. But there's an awful lot of 00s in that
public key. It doesn't seem to be very random. And that's certainly an unusual
number of bits in the key. Never hurts to try to factor it!

```python
#!/usr/bin/env python3

# File: factor.py

import sympy

key = '''04:13:cf:27:35:04:00:75:00:68:00:05:5b:0e:c2:
    19:83:8d:e2:3c:00:00:01:86:00:00:00:68:00:00:
    03:93:80:f2:3d:5b:ea:1d:ed:1b:15:db:a0:47:76:
    35:45:dc:fc:75:e9:4c:71:d7:81:fd:b0:bb:b6:53:
    7a:2f:41:88:1e:89:8d:3d:e7:df:50:3d:37:28:a8:
    45:e9:df:6d:7c:60:36:68:13:cf:5b:68:19:83:8d:
    e2:3c:00:00:01:86:00:00:04:13:cf:0d:1b:93:01:
    04:00:75:00:68:00:05:5b:0e:c2:19:83:8d:e2:3c:
    00:00:01:86:00:00:00:68:01:d4:00:00:00:00:00:
    00:01:a0:00:00:00:00:00:00:03:93:80:f2:3d:5b:
    ea:1d:e4:82:01:a0:00:00:00:00:00:0d:01:38:00:
    b6:85:6f:6d:2b:51:aa:0d:02:71:6e:94:3d:44:aa:
    0f:53:c0:50:39:75:51:aa:11:13:cf:41:4e:00:00:
    00:00:0d:00:0d:04:92:00:00:04:fa:00:00:00:df:
    e5'''
key = int(key.replace('\n','').replace(' ','').replace(':',''), 16)

for div in sympy.ntheory.factor_.divisors(key):
    print('divisor:', hex(div))
```

Run it and see what happens...

```sh
divisor: 0x1
divisor: 0xd
divisor: 0x504b03041400090008000069774a01f66d602c0000001e00000008000000466c61672e747874b350735b19307a407375e1af7c08c1ceec2149842dce5267809fe3323fd6c268a23f51e58f395ff4bacc52f4504b070801f66d602c0000001e000000504b01021f001400090008000069774a01f66d602c0000001e000000080024000000000000002000000000000000466c61672e7478740a00200000000000010018000e0a43a5efa3d20100301c32c9a2d2012dd3b766e1a3d201504b050600000000010001005a000000620000001139
divisor: 0x413cf2735040075006800055b0ec219838de23c00000186000000680000039380f23d5bea1ded1b15dba047763545dcfc75e94c71d781fdb0bbb6537a2f41881e898d3de7df503d3728a845e9df6d7c60366813cf5b6819838de23c0000018600000413cf0d1b9301040075006800055b0ec219838de23c000001860000006801d400000000000001a0000000000000039380f23d5bea1de48201a000000000000d013800b6856f6d2b51aa0d02716e943d44aa0f53c050397551aa1113cf414e000000000d000d0492000004fa000000dfe5
```

That was quick! I guess they picked such a small prime to make it easy on us.

We factored out `p` and `q`. But we still have to figure out how to use these
to decrypt the message. Thankfully I found a quick writeup on how to do this:

https://0day.work/how-i-recovered-your-private-key-or-why-small-keys-are-bad/

Using the code from there, I was able to write: [optimus.py](optimus.py).
Running it created [priv.key](priv.key), a private key formatted for OpenSSL
usage.

Now let's use it to decrypt the flag and we'll be done!

```sh
$ openssl rsautl -decrypt -inkey priv.key <flag.enc
Try harder!!!
```

What?! All this way and still no flag :( But where could the flag be? There's
no way the encrypted bytes decrypt to two different values somehow.

It was at this point that one of my teammates made a very astute observation.
Remember this divisor?

    divisor: 0x504b03041400090008000069774a01f66d602c0000001e00000008000000466c61672e747874b350735b19307a407375e1af7c08c1ceec2149842dce5267809fe3323fd6c268a23f51e58f395ff4bacc52f4504b070801f66d602c0000001e000000504b01021f001400090008000069774a01f66d602c0000001e000000080024000000000000002000000000000000466c61672e7478740a00200000000000010018000e0a43a5efa3d20100301c32c9a2d2012dd3b766e1a3d201504b050600000000010001005a000000620000001139

Notice anything about the beginning of the number? Maybe converting it to
text will help you see what he saw...

```python
>>> import codecs
>>> s = codecs.decode('504b03041400090008000069774a01f66d602c0000001e00000008000000466c61672e747874b350735b19307a407375e1af7c08c1ceec2149842dce5267809fe3323fd6c268a23f51e58f395ff4bacc52f4504b070801f66d602c0000001e000000504b01021f001400090008000069774a01f66d602c0000001e000000080024000000000000002000000000000000466c61672e7478740a00200000000000010018000e0a43a5efa3d20100301c32c9a2d2012dd3b766e1a3d201504b050600000000010001005a000000620000001139', 'hex')
>>> s
b'PK\x03\x04\x14\x00\t\x00\x08\x00\x00iwJ\x01\xf6m`,\x00\x00\x00\x1e\x00\x00\x00\x08\x00\x00\x00Flag.txt\xb3Ps[\x190z@su\xe1\xaf|\x08\xc1\xce\xec!I\x84-\xceRg\x80\x9f\xe32?\xd6\xc2h\xa2?Q\xe5\x8f9_\xf4\xba\xccR\xf4PK\x07\x08\x01\xf6m`,\x00\x00\x00\x1e\x00\x00\x00PK\x01\x02\x1f\x00\x14\x00\t\x00\x08\x00\x00iwJ\x01\xf6m`,\x00\x00\x00\x1e\x00\x00\x00\x08\x00$\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00Flag.txt\n\x00 \x00\x00\x00\x00\x00\x01\x00\x18\x00\x0e\nC\xa5\xef\xa3\xd2\x01\x000\x1c2\xc9\xa2\xd2\x01-\xd3\xb7f\xe1\xa3\xd2\x01PK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x00Z\x00\x00\x00b\x00\x00\x00\x119'
```

That's a zip file magic value at the beginning! Plus we see 'Flag.txt' several
times. Let's save it so we can take a look.

```python
>>> with open('optimus.zip', 'wb') as f:
...   f.write(s)
...
210
```

Now unzip it and we're done!

```sh
$ unzip optimus.zip
Archive:  optimus.zip

caution:  zipfile comment truncated
[optimus.zip] Flag.txt password:
```

...

...

...

All hope's not lost yet! Zips are usually pretty easy to crack. Let's feed it
to john (the ripper).

```sh
$ zip2john -a Flag.txt out.zip >zip.hash
Using file Flag.txt as an 'ASCII' quick check file
ver 14  out.zip->Flag.txt PKZIP Encr: cmplen=44, decmplen=30, crc=606DF601
$ john zip.hash
Loaded 1 password hash (PKZIP [32/64])
Will run 16 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
123123           (out.zip)
1g 0:00:00:00 DONE 2/3 (2017-12-18 02:06) 16.66g/s 1289Kp/s 1289Kc/s 1289KC/s 123456..gbby
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

That wasn't bad at all. Now let's unzip it and get the flag:

```sh
$ unzip optimus.zip
Archive:  optimus.zip

caution:  zipfile comment truncated
[optimus.zip] Flag.txt password:
  inflating: Flag.txt
$ cat Flag.txt
3DS{Pr1m3_numb3rs_4re_c00l!!!}
```
