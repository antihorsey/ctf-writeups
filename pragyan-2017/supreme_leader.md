Supreme Leader
=========
```
North Korea reportedly has a bioweapon in the making. Hack into their database and steal it.
Link : http://139.59.62.216/supreme_leader
```

Visiting the site a pretty blank page considering this was a web challenge. However looking at the cookies, you could see 
that a cookie with name KimJongUn was set with a value of 'TooLateNukesGone'. The "late" part of the cookie was supposed to be a 
hint about the cookie being overwritten.

Using python requests and dumping the content headers you can see that the cookie is set to a value then overwritten with 
"TooLateNukesGone"

```python
import requests

r = requests.get("http://139.59.62.216/supreme_leader")

for i in r.headers:
    print "{0} {1}".format(i, r.headers[i])
```
Which gives the following output:
```
Date Tue, 07 Mar 2017 02:52:34 GMT
Server Apache/2.4.7 (Ubuntu)
X-Powered-By PHP/5.5.9-1ubuntu4.20
Set-Cookie KimJongUn=2541d938b0a58946090d7abdde0d3890_b8e2e0e422cae4838fb788c891afb44f; expires=Tue, 07-Mar-2017 02:52:44 GMT; Max-Age=10, KimJongUn=TooLateNukesGone; expires=Tue, 07-Mar-2017 02:52:45 GMT; Max-Age=10
Vary Accept-Encoding
Content-Encoding gzip
Content-Length 604
Keep-Alive timeout=5, max=99
Connection Keep-Alive
Content-Type text/html
```
Grabbing the headers multiple times shows that the value of the cookie doesn't change so it's probably the flag. At this point 
"2541d938b0a58946090d7abdde0d3890_b8e2e0e422cae4838fb788c891afb44f" looked like hex but it didn't yield anything interesting
when converted to ascii. The underscore looked like a delimiter so I decided to split the hash into two hex values and check then length 
which turned out to both be 32. 

An MD5 in a hex dump is also 32 bytes long so I decided to take a shot in the dark and try cracking the hashes. I figured that 
if they were in fact hashes then the values should probably be in a rainbow table somewhere otherwise this wouldn't be solvable.
Which turned out to be the case:

pragyanctf{send_nukes}
