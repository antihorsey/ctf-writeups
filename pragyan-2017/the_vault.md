The Vault
=========

Original challenge text:

> [!@# a-z $%^ A-Z &* 0-9] [1,3]

An 1180 byte file named `file` was also attached.

The Linux utility `file` reveals this is a Keepass database:

```
$ file file
file: Keepass password database 1.x KDB, 3 groups, 4 entries, 50000 key transformation rounds
```

Strong hunch that the master password will match the challenge text
psuedo-regex. Convert it to a format that John the Ripper can work with:

```
$ keepass2john -i 4096 file > john.db
Inlining file
```

Now add a rule to your `john` config to search the specified space. 3 characters 
is pretty short, so we won't worry about optimizing by removing ASCII 
characters that are in the regex above.

```
[Incremental:PragyanVault]
File = $JOHN/ascii.chr
MinLen = 0
MaxLen = 3
```

Now let `john` get to work:

```
$ john --incremental:PragyanVault john.db
Loaded 1 password hash (KeePass [SHA256 AES 32/64 OpenSSL])
Will run 2 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
```

After anywhere from 5 to 20 minutes `john` should find the password:

```
k18              (file)
1g 0:00:06:21 DONE (2017-03-06 21:09) 0.002623g/s 68.65p/s 68.65c/s 68.65C/s k10..k18
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

The provided file is a Keepass 1.x database, which means it will only open in
Windows. Open the database in Keepass, specifying `k18` as the master password.
The database will open, revealing a single password named Flag, which holds the
flag: `pragyanctf{closed_no_more}`.