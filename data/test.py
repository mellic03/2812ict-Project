

fh = open("data/indices.txt", "r")
fh2 = open("indices2.txt", "w")


i = 0
for line in fh:

    if i < 2:
        fh2.write("%s " % (line.strip("\n")))
    else:
        fh2.write("%s\n" % (line.strip("\n")))

    i += 1

    if i == 3:
        i = 0
