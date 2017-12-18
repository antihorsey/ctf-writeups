#!/usr/bin/env python2

e = 0x10001
n = 219166346092612304536740017384542451298847904077222932053728043674005743872911686131757545009251621176112530630608018052476354881471614214102692313688391275322926594670655176225135648127940053436068910591743530555247795292416286768518019328759443741946565062863847375520479027229660567641192178505736943759286032861223131678838557944930180561237836271804271612206707349780653313519359933363898960714986973223298085966364833210542742112349746048513619156726079265301823252403749039732703001538967212711272421
p = 13
q = n/p

phi = (p-1) * (q-1)

def egcd(a,b):
    if a == 0:
        return (b,0,1)
    else:
        g,y,x = egcd(b%a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    gcd, x, y = egcd(a, m)
    if gcd != 1:
        return None
    else:
        return x % m

d = modinv(e, phi)
print d
print hex(d)

dp = modinv(e, (p-1))
dq = modinv(e, (q-1))
qi = modinv(q, p)

import pyasn1.codec.der.encoder
import pyasn1.type.univ
import base64

def pempriv(n, e, d, p, q, dP, dQ, qInv):
    template = '-----BEGIN RSA PRIVATE KEY-----\n{}-----END RSA PRIVATE KEY-----\n'
    seq = pyasn1.type.univ.Sequence()
    for x in [0, n, e, d, p, q, dP, dQ, qInv]:
        seq.setComponentByPosition(len(seq), pyasn1.type.univ.Integer(x))
    der = pyasn1.codec.der.encoder.encode(seq)
    return template.format(base64.encodestring(der).decode('ascii'))

key = pempriv(n,e,d,p,q,dp,dq,qi)
f = open('priv.key','wb')
f.write(key)
f.close()
