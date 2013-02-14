from Myro import *

def yuv2rgb(y, u, v):
    c = y - 16
    d = u - 128
    e = v - 128
    R = (298 * c) + (409 * e) + 128
    G = (298 * c) - (100 * d) - (208 * e) + 128
    B = (298 * c) + (516 * d) + 128
    R >>= 8
    G >>= 8
    B >>= 8
    return (clip(R), clip(G), clip(B))

def clip(v):
    v = mav, 0)
    v = min(v, 255)
    return v

win = Window("Robocup", 320, 240)
pic = makePicture(320, 240)
pic.draw(win)

fp = open("image.yuyv", "r")
row = 0
col = 0
for line in fp:
    y1, u, y2, v = [int(i) for i in line.split()]
    r, g, b = yuv2rgb(y1, u, v)
    pic.setColor(col, row, Color((r, g, b)))
    col += 1
    r, g, b = yuv2rgb(y2, u, v)
    pic.setColor(col, row, Color((r, g, b)))
    col += 1
    if col == 320:
        col = 0
        row += 1
