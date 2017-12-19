#!/usr/bin/env python2

from pwn import *

class Node(object):
    def __init__(self, left, op=None, right=None):
        self.left = left
        self.op = op
        self.right = right

        self.value = self._evaluate()
        self.text = self._string()

    def _evaluate(self):
        if self.op is None:
            return self.left

        left = self.left.evaluate()
        right = self.right.evaluate()

        if self.op == '+':
            return left + right
        elif self.op == '-':
            return left - right
        elif self.op == '*':
            return left * right
        elif self.op == '/':
            return left / right
        else:
            print >>sys.stderr, "don't know op '{}'".format(self.op)

    def _string(self):
        if self.op is None:
            return str(self.left)

        left = str(self.left)
        right = str(self.right)

        if self.op == '+' and self.right.op == '-':
            right = '({})'.format(right)

        if self.op == '-' and self.right.op in ['+', '-']:
            right = '({})'.format(right)

        if self.op == '*' and self.left.op in ['+','-']:
            left = '({})'.format(left)

        if self.op == '*' and self.right.op in ['+', '-', '/']:
            right = '({})'.format(right)

        if self.op == '/' and self.left.op is not None:
            left = '({})'.format(left)

        if self.op == '/' and self.right.op is not None:
            right = '({})'.format(right)

        return left + self.op + right

    def evaluate(self):
        return self.value

    def __str__(self):
        return self.text

    def __repr__(self):
        if self.op is None:
            return 'Node({})'.format(repr(self.left))

        else:
            return 'Node({}, {}, {})'.format(repr(self.left), self.op, repr(self.right))

def solve(target, digit):
    seen = set()

    shortest = {}

    n = digit
    for i in range(4):
        shortest[n] = Node(n)
        n *= 10
        n += digit

    while True:
        next_shortest = dict(shortest)

        for lhs in shortest.itervalues():
            for op in '+-*/':
                for rhs in shortest.itervalues():
                    if op == '/' and rhs.evaluate() == 0:
                        continue

                    node = Node(lhs, op, rhs)

                    text = str(node)
                    value = node.evaluate()

                    if len(text) >= 32:
                        continue

                    if value == target:
                        return node

                    if value in next_shortest and len(str(next_shortest[value])) < len(text):
                        continue

                    next_shortest[value] = node

        shortest = next_shortest

tube = remote('sdp01.3dsctf.org', 8003)

# intro text
tube.recvuntil(':')

# Type 'start' to start:
tube.recvuntil(':')
tube.sendline('start')

# Let's go.....
tube.recvline()
tube.recvline()

i = 0
while True:
    # [+] Challenge 1 - The number 1 using only the digit 6:
    challenge = tube.recvuntil(':')
    print challenge.rstrip()
    words = challenge.split()

    target = int(words[6])
    digit = int(words[11][:-1])

    answer = solve(target, digit)

    print str(answer)
    tube.sendline(str(answer))

    # [+] Correct!
    print tube.recvline().rstrip()
    print tube.recvline().rstrip()

    i += 1

    if i == 100:
        # Would you like to continue playing?
        print tube.recvline().rstrip()
        tube.sendline('yes')

tube.interactive()
