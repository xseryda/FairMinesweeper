from random import randint


class GameStructures:
    def __init__(self, width, height, mines):
        self.freeBoxes = width * height

        self.generateMatrix(self.freeBoxes, width, height, mines)

        self.freeBoxes -= mines
        self.mines = mines

    def load(self, matrix, visibleMatrix, mines):
        self.matrix = matrix
        self.visibleMatrix = visibleMatrix
        self.mines = mines

    def generateMatrix(self, freeBoxes, width, height, mines):
        # Mines -1, free spaces 1 #

        matrix = [[1] * (width + 2) for _ in range(height + 2)]  # matrix has safety zone around
        visibleMatrix = [[0] * (width + 2) for _ in range(height + 2)]  # matrix has safety zone around
        zeroRowCounts = [width for _ in range(height + 1)]

        for k in range(mines):
            newMine = randint(1, freeBoxes)
            i = height
            j = width
            #         print(newMine, freeBoxes, zeroRowCounts[i], k)
            pom = freeBoxes
            while pom >= newMine:  # Find correct line
                pom -= zeroRowCounts[i]
                i -= 1
            i += 1
            pom += zeroRowCounts[i]
            while pom > newMine or matrix[i][j] == 0:  # Find correct box in the line
                pom -= matrix[i][j]
                j -= 1
            matrix[i][j] -= 1
            zeroRowCounts[i] -= 1
            freeBoxes -= 1
            #         print(i,j)
        matrix[0][:] = [-5 for _ in range(width + 2)]
        matrix[height + 1][:] = [-5 for _ in range(width + 2)]
        for i in range(1, height + 1):
            matrix[i][0] = -5
            matrix[i][width + 1] = -5  # Differentiate safety zone around
        # matrix[:][0]=[-1 for i in range(height+2)]
        # matrix[1:height][width+1]=[-1 for i in range(height)]
        for i in range(1, height + 1):
            for j in range(1, width + 1):
                matrix[i][j] -= 1  # set mines to -1 and free spaces to 0
        for i in range(1, height + 1):
            for j in range(1, width + 1):
                if matrix[i][j] == -1:
                    for k in range(-1, 2):
                        matrix[i + 1][j + k] += increaseNeighbour(matrix, i + 1, j + k)
                    matrix[i][j - 1] += increaseNeighbour(matrix, i, j - 1)
                    matrix[i][j + 1] += increaseNeighbour(matrix, i, j + 1)
                    for k in range(-1, 2):
                        matrix[i - 1][j + k] += increaseNeighbour(matrix, i - 1, j + k)

                        #     print(width, height, mines, matrix)
        self.matrix = matrix
        self.visibleMatrix = visibleMatrix

    def uncoverBox(self, i, j, flag=False):
        if flag:
            self.visibleMatrix[i][j] = 2
        elif self.visibleMatrix[i][j] == 1:
            print('You already uncovered this box.')
        else:
            self.visibleMatrix[i][j] = 1
            self.freeBoxes -= 1
            if self.matrix[i][j] == -1:
                return False  # You Lost
            if self.matrix[i][j] == 0:
                self.uncoverWave(i, j)
            return True

    def uncoverWave(self, i, j):
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                if (self.visibleMatrix[k][l] == 0) and (self.matrix[k][l] > -1):
                    if self.matrix[k][l] == 0:
                        self.visibleMatrix[k][l] = 1
                        self.freeBoxes -= 1
                        self.uncoverWave(k, l)
                    else:
                        self.visibleMatrix[k][l] = 1
                        self.freeBoxes -= 1


def increaseNeighbour(matrix, i, j):
    if matrix[i][j] < 0:
        return 0
    else:
        return 1
