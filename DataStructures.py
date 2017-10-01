from random import randint


class Box:
    def __init__(self,solved,unknownSet, modified, toSolve):
        self.solved = solved
        self.unknownSet = unknownSet
        self.modified = modified
        self.toSolve = toSolve


class GameStructures:
    def __init__(self, width, height, mines):
        self.freeBoxes = width * height

        self.width = width
        self.height = height

        self.matrix = []
        self.visibleMatrix = []
        self.determinableMatrix = []
        self.uncoveredMatrix = [] # matrix of Box class instances
        self.determinable = 0
        self.uncovered = 0
        self.generateMatrix(self.freeBoxes, width, height, mines)

        self.freeBoxes -= mines
        self.mines = mines


    def load(self, matrix, visibleMatrix, mines):
        self.matrix = matrix
        self.visibleMatrix = visibleMatrix
        self.mines = mines

    def generateMatrix(self, freeBoxes, width, height, mines):
        """
        Generate matrices and place mines.
        self.matrix has >-1 in empty boxes, -1 when mine is present, -2 in boundary boxes
        self.visibleMatrix has 0 when invisible, 1 when uncovered and 2 when flagged
        self.determinableMatrix has 0 when indeterminable, 1 when determinable mine, 2 when determinable blank box
        """

        matrix = [[1] * (width + 2) for _ in range(height + 2)]  # matrix has safety zone around
        visibleMatrix = [[0] * (width + 2) for _ in range(height + 2)]  # matrix has safety zone around
        determinableMatrix = [[0] * (width + 2) for _ in range(height + 2)]  # matrix has safety zone around
        uncoveredMatrix = [[None] * (width + 2) for _ in range(height + 2)]  # matrix has safety zone around
        zeroRowCounts = [width for _ in range(height + 1)]

        # place mine
        for k in range(mines):
            newMine = randint(1, freeBoxes)
            i = height
            j = width
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

        matrix[0][:] = [-2 for _ in range(width + 2)]
        matrix[height + 1][:] = [-2 for _ in range(width + 2)]
        for i in range(1, height + 1):
            matrix[i][0] = -2
            matrix[i][width + 1] = -2  # Differentiate safety zone around
        # matrix[:][0]=[-1 for i in range(height+2)]
        # matrix[1:height][width+1]=[-1 for i in range(height)]
        for i in range(1, height + 1):
            for j in range(1, width + 1):
                matrix[i][j] -= 1  # set mines to -1 and free spaces to 0

        self.matrix = matrix
        self.visibleMatrix = visibleMatrix
        self.determinableMatrix = determinableMatrix
        self.uncoveredMatrix = uncoveredMatrix

        for i in range(1, height + 1):
            for j in range(1, width + 1):
                if matrix[i][j] == -1: # here is mine, add 1 to neighbours
                    self.increaseNeighbourNumbers(i,j)

        #     print(width, height, mines, matrix)

    def increaseNeighbourNumbers(self, i, j, amount=1):
        matrix = self.matrix

        for k in range(-1, 2):
            matrix[i + 1][j + k] += self.increaseNeighbour(matrix, i + 1, j + k, amount)
        matrix[i][j - 1] += self.increaseNeighbour(matrix, i, j - 1, amount)
        matrix[i][j + 1] += self.increaseNeighbour(matrix, i, j + 1, amount)
        for k in range(-1, 2):
            matrix[i - 1][j + k] += self.increaseNeighbour(matrix, i - 1, j + k, amount)

    def increaseNeighbour(self,matrix, i, j, amount):
        if matrix[i][j] < 0:
            return 0
        else:
            return amount

    def uncoverBox(self, i, j, flag=False):
        if flag:
            self.visibleMatrix[i][j] = 2
            self.determinable -= 1
        elif self.visibleMatrix[i][j] == 1:
            print('You already uncovered this box.')
        else:
            self.visibleMatrix[i][j] = 1
            self.freeBoxes -= 1

            if self.determinable > 0 and self.determinableMatrix[i][j] == 0:
                self.matrix[i][j] = -1
                return False # You Lost

            if self.determinableMatrix[i][j] == 2:
                self.determinable -= 1
            self.determinableMatrix[i][j] = 2
            placeMine = False
            if self.matrix[i][j] == -1: # we have to move this mine, because it was not determinable
                self.calculateNeighbours(i,j)
                placeMine = True

            knownMines, unknownSet = self.getUnknownSet(i, j)
            self.uncoveredMatrix[i][j] = Box(solved=False, unknownSet=unknownSet,
                                             modified=True, toSolve=self.matrix[i][j] - knownMines)

            self.updateStatusWave(i,j)

            if placeMine:
                self.moveMine(i,j)

            if self.matrix[i][j] == 0:
                self.uncoverWave(i, j)
            self.determinableWave()
            return True

    def calculateNeighbours(self,i,j):
        self.matrix[i][j] = 0
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                if self.matrix[k][l] == -1:
                    self.matrix[i][j] += 1

    def uncoverWave(self, i, j):
        modified = False
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                if (self.visibleMatrix[k][l] == 0) and (self.matrix[k][l] > -1):
                    modified = True
                    if self.matrix[k][l] == 0:
                        self.visibleMatrix[k][l] = 1
                        if self.determinableMatrix[k][l] == 2:
                            self.determinable -= 1
                        self.determinableMatrix[k][l] = 2
                        self.freeBoxes -= 1
                        self.uncoverWave(k, l)
                    else:
                        self.visibleMatrix[k][l] = 1
                        if self.determinableMatrix[k][l] == 2:
                            self.determinable -= 1
                        self.determinableMatrix[k][l] = 2
                        self.freeBoxes -= 1
                        knownMines, unknownSet = self.getUnknownSet(k, l)
                        self.uncoveredMatrix[k][l] = Box(solved=False, unknownSet=unknownSet,
                                                         modified=True, toSolve=self.matrix[k][l]-knownMines)
        if modified:
            self.updateUnknownSets()

    def updateUnknownSets(self):
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                box = self.uncoveredMatrix[i][j]
                if box and box.modified and not box.solved:
                    for k in range(i - 1, i + 2):
                        for l in range(j - 1, j + 2):
                            if self.determinableMatrix[k][l] > 0:
                                try:
                                    box.unknownSet.remove([k,l])
                                    if self.determinableMatrix[k][l] == 1:  # mine
                                        box.toSolve -= 1
                                except ValueError:
                                    pass

    def updateStatusWave(self, i, j):
        self.uncoveredMatrix[i][j].modified = True
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                box = self.uncoveredMatrix[k][l]
                if box is not None and box.solved == False and box.modified == False:
                    self.updateStatusWave(k,l)

        # the affected boxes are up to 2 neighbours away from the last uncovered box
        for k in range(i - 2, i + 3):
            for l in range(j - 2, j + 3):
                try:
                    box = self.uncoveredMatrix[k][l]
                    if box is not None:
                        box.modified == True
                except IndexError: #safety zone not big enough
                    pass

    def moveMine(self, fromX, fromY):
        # print ('PLACEMINE')

        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                if self.matrix[i][j] > -1 and self.determinableMatrix[i][j] == 1: # here should be mine, but is not
                    self.matrix[i][j] == -1
                    self.increaseNeighbourNumbers(i,j)
                    # fix the original mine neighbours
                    self.increaseNeighbourNumbers(fromX, fromY, amount=-1)
                    return True

        candidates = []
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                if self.visibleMatrix[i][j] == 1 and self.matrix[i][j] > 0: # number visible
                    candidate = []
                    neighbourMines = 0
                    for k in range(i - 1, i + 2):
                        for l in range(j - 1, j + 2):
                            if self.matrix[k][l] == -1:
                                neighbourMines += 1
                            if self.determinableMatrix[k][l] == 0 \
                                    and self.matrix[k][l] > -1: # nondeterminable, nonboundary, nonmine
                                candidate.append(k*self.width+l)
                    if neighbourMines < self.matrix[i][j]:
                        # print ('NEED CHANGE')
                        candidates.append(candidate)

        if not candidates:
            for i in range(1, self.height + 1):
                for j in range(1, self.width + 1):
                    if self.determinableMatrix[i][j] == 0 and self.matrix[i][j] > -1:
                        possibleCandidate = True
                        for k in range(i - 1, i + 2):
                            if not possibleCandidate:
                                break
                            for l in range(j - 1, j + 2):
                                if self.visibleMatrix[k][l] == 1 and self.matrix[k][l] > 0: # number visible
                                    possibleCandidate = False
                                    break
                        if possibleCandidate:
                            candidates.append(i*self.width+j)
            # print ('CANDIDATES', candidates)
        else:
            candidates = set.intersection(*map(set,candidates))
        if not candidates:
            print ('ERROR')
        else:
            box = candidates.pop() - 1 # 110 = row 10, column 10
            i = box // self.width
            j = box % self.width + 1
            # print (i,j)
            self.matrix[i][j] = -1
            self.increaseNeighbourNumbers(i, j)

        # fix the original mine neighbours
        self.increaseNeighbourNumbers(fromX, fromY, amount=-1)

    def determinableWave(self):
        changed = True
        while changed:
            changed = False
            for i in range(1, self.height + 1):
                for j in range(1, self.width + 1):
                    if self.visibleMatrix[i][j] == 1:
                        box = self.uncoveredMatrix[i][j]
                        if box and box.modified and not box.solved:
                            changed += self.processBox(box)
            self.updateUnknownSets()

    def processBox(self,box):
        # print (box.unknownSet, box.toSolve)
        changed = False
        if box.toSolve == len(box.unknownSet): # everything is a mine
            changed = True
            for i,j in box.unknownSet:
                if self.determinableMatrix[i][j] == 0:
                    self.determinable += 1
                self.determinableMatrix[i][j] = 1
            box.solved = True
        elif box.toSolve == 0: # everything is empty
            changed = True
            for i,j in box.unknownSet:
                if self.determinableMatrix[i][j] == 0:
                    self.determinable += 1
                self.determinableMatrix[i][j] = 2
            box.solved = True
        return changed

    def getUnknownSet(self, i, j):
        unknownSet = []
        knownMines = 0
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                if self.determinableMatrix[k][l] == 0 and self.matrix[k][l] > -2:
                    unknownSet.append([k,l])
                elif self.determinableMatrix[k][l] == 1:
                    knownMines += 1
        # print (knownMines, unknownSet)
        return knownMines, unknownSet
