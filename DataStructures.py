from random import randint


class Box:
    def __init__(self,solved,unknownSet, modified, toSolve):
        self.solved = solved
        self.unknownSet = unknownSet
        self.modified = modified
        self.toSolve = toSolve

class doneException(Exception):
    pass

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

        # self.generateDummy()
        self.generateMatrix(self.freeBoxes, width, height, mines)

        self.freeBoxes -= mines
        self.mines = mines

    def load(self, matrix, visibleMatrix, determinableList, determinable, mines, width, height):
        self.matrix = matrix
        self.visibleMatrix = visibleMatrix
        self.determinableMatrix = determinableList
        self.determinable = determinable
        self.mines = mines
        self.width = width
        self.height = height

    def generateDummy(self):

        self.width = 4
        self.height = 2
        #self.matrix = [[-5,-5,-5,-5,-5,-5],[-5,-1,3,-1,1,-5],[-5,-1,3,1,1,-5],[-5,-5,-5,-5,-5,-5]]

        self.width = 6
        self.height = 7
        self.matrix = [[-5,-5,-5,-5,-5,-5,-5,-5],[-5,1, 1, -1, 1, 1, -1,-5], [-5,1, 1, 1, 1, 1, 1,-5], [-5,2, 1, 0, 0, 0, 0,-5] , [-5,-1, 2, 1, 0, 0, 0,-5],
                        [-5,3, -1, 2, 1, 1, 0,-5],[-5,-1, 3, 2, -1, 1, 0,-5], [-5,-1, 2, 1, 1, 1, 0,-5],[-5,-5,-5,-5,-5,-5,-5,-5]]

        self.visibleMatrix = [[0] * (self.width + 2) for _ in range(self.height + 2)]
        self.determinableMatrix = [[0] * (self.width + 2) for _ in range(self.height + 2)]
        self.uncoveredMatrix = [[None] * (self.width + 2) for _ in range(self.height + 2)]

    def generateMatrix(self, freeBoxes, width, height, mines):
        """
        Generate matrices and place mines.
        self.matrix has >-1 in empty boxes, -1 when mine is present, -5 in boundary boxes
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

        self.matrix = matrix
        self.visibleMatrix = visibleMatrix
        self.determinableMatrix = determinableMatrix
        self.uncoveredMatrix = uncoveredMatrix

        for i in range(1, height + 1):
            for j in range(1, width + 1):
                if matrix[i][j] == -1: # here is mine, add 1 to neighbours
                    self.changeNeighbourNumbers(i, j)

        #     print(width, height, mines, matrix)

    def changeNeighbourNumbers(self, i, j, amount=1):
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
        elif self.visibleMatrix[i][j] == 1:
            print('You already uncovered this box.')
        else:
            self.freeBoxes -= 1

            if (self.determinable > 0 and self.determinableMatrix[i][j] == 0) or self.determinableMatrix[i][j] == 1:
                self.matrix[i][j] = -1
                return False # You Lost

            if self.determinableMatrix[i][j] == 2:
                self.determinable -= 1
            self.determinableMatrix[i][j] = 2
            placeMine = False
            if self.matrix[i][j] == -1: # we have to move this mine, because it was not determinable
                self.calculateNeighbours(i,j)
                self.moveMine(i, j)
                placeMine = True

            self.visibleMatrix[i][j] = 1

            knownMines, unknownSet = self.getUnknownSet(i, j)
            if self.checkUnknownSet(unknownSet,i,j):
                self.uncoveredMatrix[i][j] = Box(solved=False, unknownSet=unknownSet,
                                             modified=True, toSolve=self.matrix[i][j] - knownMines)

                # self.updateStatusWave(i,j)

            if placeMine:
                pass

            if self.matrix[i][j] == 0:
                if self.uncoverWave(i, j):
                    self.updateUnknownSets()
            self.determinableWave()
            return True

    def calculateNeighbours(self,i,j):
        self.matrix[i][j] = 0
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                if self.matrix[k][l] == -1:
                    self.matrix[i][j] += 1

    def getUnknownSet(self, i, j):
        # unknownSet = []
        unknownSet = set()
        knownMines = 0
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                if self.determinableMatrix[k][l] == 0 and self.matrix[k][l] > -2:
                    #unknownSet.append([k,l])
                    unknownSet.add(k*self.width+l)
                elif self.determinableMatrix[k][l] == 1:
                    knownMines += 1
        # print (knownMines, unknownSet)
        return knownMines, unknownSet

    def checkUnknownSet(self, unknownSet, i, j):
        """
        Check if we already know about this set, have to look in the 2 distance for equality.
        :param unknownSet: unknownSet of new box
        :param i: x index of new box
        :param j: y index of new box
        :return: True if this set is unknown else False
        """
        if not unknownSet:
            return False
        for k in range(i - 2, i + 3):
            for l in range(j - 2, j + 3):
                try:
                    box = self.uncoveredMatrix[k][l]
                    if box and box.unknownSet == unknownSet:

                        return False
                except IndexError: #safety zone not big enough
                    pass
        # print ('DIFFERENT', unknownSet)
        return True

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
                        if self.checkUnknownSet(unknownSet, k, l):
                            self.uncoveredMatrix[k][l] = Box(solved=False, unknownSet=unknownSet,
                                                         modified=True, toSolve=self.matrix[k][l]-knownMines)
        return modified

    def updateUnknownSets(self):
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                box = self.uncoveredMatrix[i][j]
                if box and box.modified and not box.solved:
                    for k in range(i - 1, i + 2):
                        for l in range(j - 1, j + 2):
                            if self.determinableMatrix[k][l] > 0:
                                try:
                                    # box.unknownSet.remove([k,l])
                                    box.unknownSet.remove(k*self.width+l)
                                    if self.determinableMatrix[k][l] == 1:  # mine
                                        box.toSolve -= 1
                                # except ValueError:
                                except KeyError:
                                    pass
                    # box.modified = False

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
                        box.modified = True
                except IndexError: #safety zone not big enough
                    pass

    def moveMine(self, fromX, fromY):
        # TODO opravit

        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                if self.matrix[i][j] > -1 and self.determinableMatrix[i][j] == 1: # here should be mine, but is not
                    print ('Situation 1')
                    self.matrix[i][j] = -1
                    self.changeNeighbourNumbers(i, j)
                    # fix the original mine neighbours
                    self.changeNeighbourNumbers(fromX, fromY, amount=-1)
                    return True

        candidates = [] #some fields are missing mine around
        antiCandidates = [] #some fields uncovered but not missing a mine
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                if self.visibleMatrix[i][j] == 1 and self.matrix[i][j] > 0: # number visible
                    candidate = []
                    antiCandidate = []
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
                    else:
                        antiCandidates += candidate
        newMines = self.processCandidates(candidates, set(antiCandidates))

        if newMines:
            self.placeMines(newMines)
            self.removeMines(len(newMines)-1, antiCandidates)
            # fix the original mine neighbours
            self.changeNeighbourNumbers(fromX, fromY, amount=-1)
            return

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

        if not candidates:
            print('ERROR')
        else:
            self.placeMines([candidates.pop()])

        # fix the original mine neighbours
        self.changeNeighbourNumbers(fromX, fromY, amount=-1)

    def placeMines(self, newMines):
        for newMine in newMines:
            newMine -= 1 # 110 = row 10, column 10
            i = newMine // self.width
            j = newMine % self.width + 1
            self.matrix[i][j] = -1
            self.changeNeighbourNumbers(i, j)

    def removeMines(self, number, antiCandidates):
        if number == 0:
            return
        #TODO improve - duplicite code for possibleCandidate and randomness of mine deletion
        try:
            for i in range(1, self.height + 1):
                for j in range(1, self.width + 1):
                    if self.determinableMatrix[i][j] == 0 and self.matrix[i][j] == -1:
                        possibleCandidate = True
                        for k in range(i - 1, i + 2):
                            if not possibleCandidate:
                                break
                            for l in range(j - 1, j + 2):
                                if self.visibleMatrix[k][l] == 1 and self.matrix[k][l] > 0:  # number visible
                                    possibleCandidate = False
                                    break
                        if possibleCandidate:
                            self.matrix[i][j] = 0
                            self.changeNeighbourNumbers(i, j, amount=-1)
                            self.calculateNeighbours(i,j)
                            number -= 1
                            if number == 0:
                                raise doneException
        except doneException:
            return

    def determinableWave(self):
        self.updateUnknownSets()
        changed = True
        while changed:
            # print('determinableWave')
            changed = False
            for i in range(1, self.height + 1):
                for j in range(1, self.width + 1):
                    if self.visibleMatrix[i][j] == 1:
                        box = self.uncoveredMatrix[i][j]
                        if box and box.modified and not box.solved:
                            # print (i,j)
                            changed += self.processBox(box,i,j)
            self.updateUnknownSets()

    def processCandidates(self, candidates, antiCandidates):
        newMines = []
        removeIndices = []
        #indicesOfCandidates = {} #dict based on 'reversed' candidates - candidate is key, indices of candidates is value
        for i,candidate in enumerate(candidates):
            candidates[i] = [item for item in candidate if item not in antiCandidates]
            #for item in candidates[i]:
            #    #TODO improve
            #    try:
            #        indicesOfCandidates[item].append(i)
            #    except:
            #        indicesOfCandidates[item] = [i]
        #print (candidates)
        #print ('INDICES', indicesOfCandidates)



        for candidate in candidates:
            if len(candidate) == 1:
                mine = candidate[0]
                newMines.append(mine)

                for i,deletecandidate in enumerate(candidates):
                    if mine in deletecandidate:
                        removeIndices.append(i)
        for i in reversed(sorted(removeIndices)):
            candidates.pop(i)
                    #TODO indices would change -- would not work this way
                    #for i in indicesOfCandidates[candidate[0]]:
                    #    print (i)
                    #    candidates.pop(i)

        #print('CANDI', candidates)
        #print('ANTI', antiCandidates)
        #print('NEWMINES', newMines)
        if candidates:
            candidates = set.intersection(*map(set,candidates))
            if candidates:
                newMines.append(candidates.pop())

        return newMines



    def processBox(self, box, boxi, boxj):
        # print (box.unknownSet, box.toSolve, boxi, boxj)
        changed = False
        if box.toSolve == len(box.unknownSet): # everything is a mine
            changed = True
            for coord in box.unknownSet:
                i = (coord-1) // self.width # 110 = row 10, column 10
                j = (coord-1) % self.width + 1
                self.determinableMatrix[i][j] = 1
            box.solved = True
            # del box
        elif box.toSolve == 0: # everything is empty
            changed = True
            for coord in box.unknownSet:
                i = (coord-1) // self.width # 110 = row 10, column 10
                j = (coord-1) % self.width + 1
                if self.determinableMatrix[i][j] == 0:
                    self.determinable += 1
                self.determinableMatrix[i][j] = 2
            box.solved = True
            # del box
        else:
            for k in range(boxi - 2, boxi + 3):
                for l in range(boxj - 2, boxj + 3):
                    if k != boxi or l != boxj:
                        try:
                            Neighbox = self.uncoveredMatrix[k][l]
                            if Neighbox and not Neighbox.solved:
                                AaB = Neighbox.unknownSet & box.unknownSet
                                if not AaB:  # no intersection
                                    # print('NO INTER', Neighbox.unknownSet, box.unknownSet)
                                    continue
                                elif Neighbox.unknownSet == box.unknownSet: # some neighbor has the same set
                                    Neighbox.solved = True
                                    # print ('SAME')
                                    continue
                                elif Neighbox.unknownSet > box.unknownSet:
                                    Neighbox.unknownSet = Neighbox.unknownSet - box.unknownSet
                                    Neighbox.toSolve -= box.toSolve
                                    changed = True
                                    # print ('SUPERSET')
                                else:
                                    AmB = box.unknownSet - Neighbox.unknownSet
                                    BmA = Neighbox.unknownSet - box.unknownSet
                                    if Neighbox.toSolve + len(AmB) == box.toSolve:
                                        changed = True
                                        for coord in AmB:
                                            i = (coord - 1) // self.width  # 110 = row 10, column 10
                                            j = (coord - 1) % self.width + 1
                                            self.determinableMatrix[i][j] = 1 #mine
                                        for coord in BmA:
                                            i = (coord - 1) // self.width  # 110 = row 10, column 10
                                            j = (coord - 1) % self.width + 1
                                            if self.determinableMatrix[i][j] == 0:
                                                self.determinable += 1
                                            self.determinableMatrix[i][j] = 2 #empty
                                        box.solved = True
                                        Neighbox.unknownSet = AaB # intersection
                                    # TODO compute the inverse operation here for optimization?

                        except IndexError:  # safety zone not big enough
                            pass

        return changed
