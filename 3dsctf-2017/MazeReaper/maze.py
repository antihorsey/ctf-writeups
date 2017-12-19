#!/usr/bin/env python2

from pwn import *

class Room(object):
    def __init__(self, index):
        self.index = index
        self.keys = ''
        self.locks = ''
        self.connections = set()
        self.start = False
        self.exit = False

def add_key(key, keys):
    return ''.join(sorted(list(set(key + keys))))

def read_problem(tube):
    nr, NC, NK, ND = map(int, tube.recvline().split())

    print 'rooms: {}     keys: {}    doors: {}'.format(nr, NK, ND)

    rooms = [Room(i) for i in range(nr)]

    SP, EP = map(int, tube.recvline().split())
    rooms[SP].start = True
    rooms[EP].exit = True

    for i in range(NC):
        a, b = map(int, tube.recvline().split())
        rooms[a].connections.add(b)
        rooms[b].connections.add(a)

    for i in range(NK):
        words = tube.recvline().split()
        room, key = int(words[0]), words[1]
        rooms[room].keys = add_key(key.upper(), rooms[room].keys)

    for i in range(ND):
        words = tube.recvline().split()
        room, lock = int(words[0]), words[1]
        rooms[room].locks = add_key(lock.upper(), rooms[room].locks)

    return rooms

def solve(rooms):
    seen = set()
    q = []

    for room in rooms:
        if room.start:
            q.append((room.index, '', 0))
            seen.add((room.index, ''))

    while q:
        index, keys, n = q[0]
        q = q[1:]

        room = rooms[index]
        for conn in room.connections:
            other = rooms[conn]
            next_keys = add_key(keys, other.keys)

            if (conn, next_keys) in seen:
                continue

            access = True
            for lock in other.locks:
                if lock not in keys:
                    access = False
                    break

            if not access:
                continue

            if other.exit:
                return n + 1

            seen.add((conn, next_keys))
            q.append((conn, next_keys, n+1))

    return -1

tube = remote('maze01.3dsctf.org', 8002)

tube.recvuntil("Type 'start' for try to runaway:")
tube.sendline('start')

while True:
    # Challenge 1:
    print tube.recvuntil(':').rstrip()
    print tube.recvline().rstrip()

    rooms = read_problem(tube)
    answer = solve(rooms)

    # The answer is:
    print tube.recvuntil(':').rstrip()
    print answer
    tube.sendline(str(answer))
