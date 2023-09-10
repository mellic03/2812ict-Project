


fh = open("data/face_index_buffer copy.txt", "r")
fh2 = open("indices.txt", "w")


i = 0
for line in fh:
    fh2.write(line)
    i += 1
    if i == 3:
        fh2.write("\n")
        i = 0
