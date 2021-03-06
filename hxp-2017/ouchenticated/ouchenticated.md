Ouchenticated
=============

The ouchenticated service signs then encrypts the string '{admin: 0}' and gives
us the output. Our goal is to flip the 0 to a 1 and generate a valid signature.

The signature process appends a 16-byte nonce, then computes a CRC of the whole
string. The CRC is then also appended to the string.

The encryption is AES in CTR mode.

Since the encryption is in CTR mode, changing the ciphertext to decrypt to a
different plaintext is fairly easy. The ciphertext `C` is generated by taking
the output `O` of the AES cipher and XOR-ing it with the plaintext `P`:

    O ⊕ P → C

Decryption proceeds in a similar fashion: the ciphertext `C` is XOR-ed with
the output `O` to recover the plaintext `P`:

    O ⊕ C → P

So if we want to change the `P` to a modified plaintext `P'`, we just calculate
the XOR difference `X`:

    P ⊕ P' → X

And then XOR it with C to create the modified ciphertext `C'`:

    C ⊕ X → C'

Decryption then proceeds as follows:

    O ⊕ C' = O ⊕ (C ⊕ X) = (O ⊕ C) ⊕ X = P ⊕ X = P'

So now we know how to modify the ciphertext to make it decrypt to '{admin: 1}`.
But how do we pass the signature check after modifying the ciphertext? We don't
know the nonce so we can't recompute the CRC, right?

Well I won't get into the number theory, but suffice it to say that CRC is
linear with respect to XOR. That means if you XOR two strings together, their
CRC is equal to the CRC-ing each string individually then XOR-ing the CRCs:

    CRC(A) ⊕ CRC(B) = CRC(A ⊕ B)

However, in practice most CRC algorithms (which we'll call `CRC'`) have a
nonzero starting state which must be taken into account too:

    CRC'(A) ⊕ CRC'(B) = CRC'(A ⊕ B) ⊕ CRC'(0) 

(where `0` is a string of all 0 bits of the same length as A and B).

In our case, we want to find the encrypted CRC' of the modified plaintext P'.
We don't know the original string or the original CRC', but all we need are the
encrypted forms of each, `C` and `C_crc`. Having these will let us
calculate the encrypted CRC' of the modified ciphertext which we'll call
C_crc'.

    C_crc' = O ⊕ CRC'(P') = O ⊕ CRC'(P ⊕ X) = O ⊕ CRC'(P) ⊕ CRC'(X) ⊕ CRC'(0)
    O ⊕ CRC'(P) ⊕ CRC'(X) ⊕ CRC'(0) = C_crc ⊕ CRC'(X) ⊕ CRC'(0)

We're given C_crc and can calculate CRC'(X) and CRC'(0).

Now we have everything we need. We can calculate the XOR difference between the
original plaintext and the modified plaintext and use that to generate a
modified ciphertext and signature that will pass signature verification.

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
