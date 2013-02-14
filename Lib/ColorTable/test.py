def vote(matrix, width, height, i):
    votes = {}
    count = {}
    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            p = (i + x) + y * width
            col = p % width
            row = p // width
            if 0 <= col < width and 0 <= row < height:
                votes[matrix[p]] = votes.get(matrix[p], 0) + 1
    m = max(votes.values())
    if m > 4:
        return votes.keys()[votes.values().index(m)]
    else:
        return 0

def convolve(matrix, width, height):
    newmatrix = [0] * len(matrix)
    for i in range(len(matrix)):
        newmatrix[i] = vote(matrix, width, height, i)
    return newmatrix

matrix = [8, 8, 8,
          1, 8, 0,
          1, 8, 8]

#print vote(matrix, 3, 3, 4)
print convolve(matrix, 3, 3)