cipher       = '6(#KM5_3KYG^~]O"9q#O4KLsbE{_yri|6(5SDjll`%J:'
plain        = '"So,_did_you_hold_back_during_thattest?""May'

flag_cipher  = ')J"<E9o.cOMU%T!$NB/!0U`tLrqERuaG4(g.EUyM2?z>'
flag_plain   = ''

table = []

with open('table.tsv','r') as f:
    for line in f:
        row = ''

        line = line.rstrip()
        for i in range(0, len(line), 2):
            row += line[i]

        table.append(row[1:])

table = table[1:]

for i in range(len(cipher)):
    c = cipher[i]
    p = plain[i]
    f = flag_cipher[i]

    ndx = table[0].find(p)
    for row in table:
        if row[ndx] == c:
            flag_plain += table[0][row.find(f)]

print flag_plain
