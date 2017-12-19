Escape from Arkham I
===

This challenge came with 12 keyfiles attached. Inspecting more closely with
`file` and `cat`, we see that 10 are a triple of points like:

`(1, 151648841525131405667174586591517337090635368623348815925544815009261895198612, 107794757594075833151238056001942203657877423915508846053340735546290486113897)`

The 11th, master.key, is a binary OpenSSL-encrypted file. The 12th,
the_joker.key, looks like it's base-64 encoded:

```sh
$ cat keys/the_joker.key
SEEgSEEgSEEgSEEgSEEgSEEgSEEgSEEgSEEgSEEgSEEgSEEgSEEgSEEgSEENCg0KV0hBVCBBIEpPS0UhDQoNCllvdSB0aG91Z2h0IHRoYXQgaXQgd291bGQgYmUgc28gZWFzeT8NCg0KWW91IGFpbid0IG5vIEJhdHN5ISEhISBIZSdzIGEgdHJ1ZSBkZXRlY3RpdmUhIFlvdSBhcmUganVzdC4uLiBobW1tLi4uIGFsaXZlLCBhbmQgSSBkb24ndCBrbm93IHdoeS4uLg0KDQpSZWFsbHksIHJlYWxseSBmdW5ueS4uLi4NCg0KSW4gZmFjdCwgbGV0J3MgcGxheSBhIGdhbWUgc2luY2UgdGhpcyBpcyBhbGwgYSBiaWcgam9rZS4uLi4gDQoNClRoZSBtYXN0ZXIga2V5IHdhcyBjaXBoZXJlZCB1c2luZyBhZXMtMjU2LWNiYyBvbiBPcGVuU1NMIDEuMS4wZyAyIE5vdiAyMDE3DQoNCkVuam95IHlvdXIgdGFpbCBjaGFzaW5nLCBiZWNhdXNlIHdoZW4gQmF0c3kgYXJyaXZlcywgSSdsbCBub3QgYmUgaGVyZSEhDQoNCkhBIEhBIEhBIEhBIEhBIEhBIEhBIEhBIEhBIEhBIEhBIEhBIEhBIEhBIEh
$ base64 -d <keys/the_joker.key >the_joker.txt
$ file the_joker.txt
the_joker.txt: ASCII text, with CRLF line terminators
$ cat the_joker.txt
HA HA HA HA HA HA HA HA HA HA HA HA HA HA HA

WHAT A JOKE!

You thought that it would be so easy?

You ain't no Batsy!!!! He's a true detective! You are just... hmmm... alive, and I don't know why...

Really, really funny....

In fact, let's play a game since this is all a big joke....

The master key was ciphered using aes-256-cbc on OpenSSL 1.1.0g 2 Nov 2017

Enjoy your tail chasing, because when Batsy arrives, I'll not be here!!

HA HA HA HA HA HA HA HA HA HA HA HA HA HA HA
```

Looks like in the manner of most movie villains, the Joker gave us (almost)
all the exact details of how he encrypted the key.

Well, first things first. The problem mentioned sharing a secret amongst
multiple people, so the first thing that comes to mind is
[Shamir's Secret Sharing algorithm](https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing).
And sure enough, in this algorithm the secret is split into a set of points,
which is exactly what we have.

A quick Google search finds a Python library named secretsharing which
implements Shamir's algorithm. Using it is pretty straightforward, everything
just worked, and we got the integer
191881421901048827297611928646982000903180189011441676325972065. Converting
it to hex gives a number that suspiciously looks like ASCII:

```py
>>> hex(191881421901048827297611928646982000903180189011441676325972065)
'0x7768795f736f5f63727970746f3f5f68615f68615f68615f6861L'
>>> '7768795f736f5f63727970746f3f5f68615f68615f68615f6861'.decode('hex')
'why_so_crypto?_ha_ha_ha_ha'
```

We've got the key! We've got the exact cipher parameters used! We're done
right?

```sh
$ openssl enc -in keys/master.key -d -k 'why_so_crypto?_ha_ha_ha_ha' -aes-256-cbc >master.dec
bad decrypt
140397014208448:error:06065064:digital envelope routines:EVP_DecryptFinal_ex:bad decrypt:crypto/evp/evp_enc.c:536:
```

Nope, apparently not. Enter me beating my head against a wall for the next hour
trying to figure out what the problem was. Fast forward to me finally figuring
out what worked: specifying md5 for the key derivation function.

```sh
$ openssl enc -in keys/master.key -d -k 'why_so_crypto?_ha_ha_ha_ha' -aes-256-cbc -md md5 >master.dec
$ file master.dec
master.dec: PNG image data, 300 x 30, 8-bit/color RGBA, non-interlaced
$ mv master.dec master.png
```

Opening the PNG reveals the flag:

![Sh4m1r_S4b3_S3p4r4r_S3gr3d0s](master.png)
