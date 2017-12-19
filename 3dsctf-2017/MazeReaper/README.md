MazeReaper
==========

Upon connecting to the server given in the problem statement, you are presented
with the following:

```

                    +++     3DSCTF - MAZEREAPER     +++

 [+] After being captured by the Grim Reaper, you were taken to a secret reaping
     room for the secret games of death.

                                      ...
                                    ;::::;
                                  ;::::; :;
                                ;:::::'   :;
                               ;:::::;     ;.
                              ,:::::'       ;           OOO
                              ::::::;       ;          OOOOO
                              ;:::::;       ;         OOOOOOOO
                             ,;::::::;     ;'         / OOOOOOO
                           ;:::::::::`. ,,,;.        /  / DOOOOOO
                         .';:::::::::::::::::;,     /  /     DOOOO
                        ,::::::;::::::;;;;::::;,   /  /        DOOO
                       ;`::::::`'::::::;;;::::: ,#/  /          DOOO
                       :`:::::::`;::::::;;::: ;::#  /            DOOO
                       ::`:::::::`;:::::::: ;::::# /              DOO
                       `:`:::::::`;:::::: ;::::::#/               DOO
                        :::`:::::::`;; ;:::::::::##                DO
                        ::::`:::::::`;::::::::;:::#                DO
                        `:::::`::::::::::::;'`:;::#                D
                         `:::::`::::::::;' /  / `:#
                          ::::::`:::::;'  /  /   `#

 [+] As The Death loves to play with its victims, it loosed you at the
     beginning of a maze with a map and said: "There are keys and doors
     scattered around the labyrinth.The distance between each connected room is
     unitary. number of hits possible, I will not take your soul and I will set
     you free. "

 [+] Since she released you, you have highlighted the following
     information on the map:
     - A line with four values: number of rooms (nr), number of corridors
       between rooms (NC), number of keys (NK), number of doors (ND).
     - A line with the position that The Death left you (SP) and the place of
       the exit (EP).
     - A list of NC corridors between two rooms.
     - A list of NK with key locations (lower case).
     - And a list ND with the doors (capital letters) that need keys.

 [+] Example:
                                          +-+
                                          | |
                          +---------------+-+
+-+--------+           +--+
| |        |           |SP|        +----------------+--+
+-+        |           +--+        |                |EP|
           +-+---------+  +------+-+                +--+
           |a|                   |A|                |
           +-+                   +-+                |
                                   |                |
                                   +------+-+-------+
                                          | |
                                          +-+

 [+] For the example the answer is 4.

 [+] Sometimes The Reaper plays with no escape mazes. If this occurs,
     answer with -1.

 [+] Type 'start' for try to runaway:
```

I was taken aback by the instructions at first, so let me clarify: In the image
above, in the lower right corner those are lines connecting A and EP, that's
not a giant room. The specification of that scenario would look something like:

`7 7 1 1` : 7 rooms, 7 corridors, 1 key, 1 door

`3 7` : start in room #3, exit in room #7

```
1 2
2 3
3 4
3 5
4 6
4 7
6 7
```

Corridors connecting the rooms

`2 a` : key 'a' in room #2

`4 A` : door 'A' requiring key 'a' in room #4

The shortest route would then be start in room 3 and move to room 2 to pick up
key 'a', move back to room 3, move to room 4 and unlock A, move to room 7 and
exit. A total of 4 moves.

That being said, the way to solve is pretty straightforward, at least for
problems that aren't much larger than this. Just run a standard breadth-first
search, except instead of storing just your position for the state, also store
which keys you currently have. If you've already visited a room but had a
different set of keys, then you've hit a new state and should keep that in your
search queue. If you've already visited a room and have the same set of keys,
then you've already hit this state. Since it's a breadth-first search, you know
the previous path to get there was shorter, so discard the new duplicate state.

That makes for an upper bound of R * 2<sup>K</sup> possible states, where R is
the number of rooms and K is the number of keys. The final level of this
challenge was R=200 and K=20, for an upper bound of 209,715,200 states.
Probably couldn't have done much bigger mazes than this, but this will suffice
for the challenge.

This algorithm would probably have been a lot faster if I represented the keys
and doors as bitvectors and did bitwise operations to test for access instead
of manipulating strings all over the place, but this got the job done.

Solve 50 challenges and you'll receive the following message:

```
 [+] Nice, the flag is:
 3DS{br4vElY_Fac3_th3_$oUL_r3Ap3R}
```
