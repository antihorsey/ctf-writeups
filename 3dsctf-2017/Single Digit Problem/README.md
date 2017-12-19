Single Digit Problem (plus BONUS!)
==================================

Connect to the server specified in the problem statement, and you're greeted
with the following:

```
               +++     3DSCTF - Single Digit Problem     +++

 [+] For this game, you need to type an expression that the answer is the
     requested number.

 [+] Allowed symbols: ( + - * / )

 [+] Limit of 31 characters

 [+] Numbers need to be less than 100000

 [+] Type 'start' to start:
```

After typing 'start' to continue, you're given problems like the following:

```
 [+] Challenge 1 - The number 1 using only the digit 8:
```

The target number is always the same as the challenge number, making the game
progressively harder. The chosen digit appears to be randomly selected from
1-9.

General approach: use Nodes to model the expression tree so that we know where
parentheses are needed. Each Node knows both how to evaluate its value and how
to convert itself to a string.

Keep a mapping of ints to Nodes. Start the mapping with terminal Nodes that
evaluate to `D`, `DD`, `DDD`, `DDDD`, `DDDDD`, where `D` is the digit specified
in the problem, and `DD` is the number `D * 10 + D` etc.

Repeatedly iterate over each possible pair of Nodes and each possible operator.
Each time a Node evaluates to an int that we haven't seen before or has a
shorter string representation than the previous Node that evaluated to that
int, update the mapping. Prune Nodes that have longer string representations
and Nodes that have string representations longer than 31 characters.

Continue until a Node evaluates to the target number and its string
representation is less than 32 characters.

Other than that, I'll let the code speak for itself. The parenthesis logic is
pretty janky, I'm sure there's probably a better way to have done that.

After solving 100 challenges, we get the following:

```
 [+] Challenge 100 - The number 100 using only the digit 8: 888/88*(888/88)
  [+] Correct!
 [+] WOW, the flag is: 3DS{y0U_aR3_g00d_w1TH_nUmb3rS}
```

But if we keep the connection open for a second or two we get another message!

```
 [+] Would you like to continue playing?
```

Sending 'yes' will then present us with another 900 problems! This algorithm
has a couple of scary moments where it looks like it might time out, but I've
never seen it fail to make it to the end of 1000.

```
 [+] Challenge 1000 - The number 1000 using only the digit 3: 3/3+333*3
  [+] Correct!
 [+] WOW, the flag is: 3DS{y0U_aR3_R34LLY_1nS4n3_w1TH_nUmb3rS}
```
