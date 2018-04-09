Log Search
==========

Pretty straightforward printf vulnerability. pwntools will do the
heavy lifting for us. The main key to this one is to do it
efficiently.

We could put in a lot of effort and get full execution control. But
all we need is the flag. Studying the log search function provides
us with a quicker path to the flag -- overwrite the log filename with
flag.txt, overwrite strstr with printf, and instead of searching the
log for a search query, it will print every line from the flag.

One thing to watch out for: GOT entries are pointers to executable
code and PLT entries are executable code. You can't overwrite a GOT
entry with a pointer to a GOT entry because that makes it a pointer
to a pointer to executable code. Overwriting it with an entry to
another PLT entry makes it a pointer to executable code even though
it will take you through the PLT/GOT twice. In this instance,
execution will look like: strstr@plt -> strstr@got -> printf@plt ->
printf@got -> printf@libc.
