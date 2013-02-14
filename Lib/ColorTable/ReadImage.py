import sys

fp = open(sys.argv[1], "r")
data = fp.read(8)

out = open("%s.yuyv" % sys.argv[1], "w")

while data:
    y1 = int(data[0:2], 16)
    u = int(data[2:4], 16)
    y2 = int(data[4:6], 16)
    v = int(data[6:8], 16)
    #print(y1, u, y2, v)
    out.write("%i %i %i %i\n" % (y1, u, y2, v))
    data = fp.read(8)
    
out.close()
