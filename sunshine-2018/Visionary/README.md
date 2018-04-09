Visionary
=========

Not too much to explain here, just a basic Vigenere cipher. For each
character in the supplied plaintext, we find its position in the
header row of the table. We scan through all the other rows to find
out which row has the corresponding ciphertext character in the same
position. Then we find the position of the flag's ciphertext
character in that row, and print out the corresponding character in
the header row, providing us with the flag's plaintext character.
Across, straight down, across, straight up.
