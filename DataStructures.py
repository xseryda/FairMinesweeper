from random import randint, sample


class Box:
    def __init__(self, solved, unknownSet, modified, toSolve):
        self.solved = solved
        self.unknownSet = unknownSet
        self.modified = modified
        self.toSolve = toSolve


class doneException(Exception):
    pass


class VirtualPlayer:
    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height
        self._checkedCombinations = []

        self._determinableMatrix = [[0] * (width + 2) for _ in range(height + 2)]  # matrix has safety zone around
        self._boxesToSolve = [[None] * (width + 2) for _ in range(height + 2)]  # matrix has safety zone around

    def __getitem__(self, pos):
        i, j = pos
        return self._determinableMatrix[i][j]

    def __setitem__(self, pos, value):
        i, j = pos
        self._determinableMatrix[i][j] = value

    def load(self, determinableList):
        self._determinableMatrix = determinableList

    def getBox(self, i, j):
        return self._boxesToSolve[i][j]

    def setBox(self, i, j, box):
        self._boxesToSolve[i][j] = box

    def updateUnknownSets(self):
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                box = self.getBox(i, j)
                if box and box.modified and not box.solved:
                    for k in range(i - 1, i + 2):
                        for l in range(j - 1, j + 2):
                            if self[k, l] > 0:
                                try:
                                    # box.unknownSet.remove([k,l])
                                    box.unknownSet.remove(k * self.width + l)
                                    if self[k, l] == 1:  # mine
                                        box.toSolve -= 1
                                # except ValueError:
                                except KeyError:
                                    pass
                                    # box.modified = False

    def updateStatusWave(self, i, j):
        self.getBox(i, j).modified = True
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                box = self.getBox(k, l)
                if box is not None and box.solved == False and box.modified == False:
                    self.updateStatusWave(k, l)

        # the affected boxes are up to 2 neighbours away from the last uncovered box
        for k in range(i - 2, i + 3):
            for l in range(j - 2, j + 3):
                try:
                    box = self.getBox(k, l)
                    if box is not None:
                        box.modified = True
                except IndexError:  # safety zone not big enough
                    pass

    def removeBox(self, box):
        self._boxesToSolve.remove(box)

    def processBox(self, box, boxi, boxj):
        # print (box.unknownSet, box.toSolve, boxi, boxj)
        changed = False
        determinable = 0
        newMinesCandidates, removedMinesCandidates = [], []
        if box.toSolve == len(box.unknownSet): # everything is a mine
            changed = True
            for coord in box.unknownSet:
                i = (coord-1) // self.width # 110 = row 10, column 10
                j = (coord-1) % self.width + 1
                newMinesCandidates.append([i, j])
                #print (i, j)
                self[i, j] = 1
            box.solved = True
            # del box
        elif box.toSolve == 0: # everything is empty
            changed = True
            for coord in box.unknownSet:
                i = (coord-1) // self.width # 110 = row 10, column 10
                j = (coord-1) % self.width + 1
                if self[i, j] == 0:
                    determinable += 1
                    removedMinesCandidates.append([i, j])
                #print (i, j)
                self[i, j] = 2
            box.solved = True
            # del box
        else:
            for k in range(boxi - 2, boxi + 3):
                for l in range(boxj - 2, boxj + 3):
                    if k != boxi or l != boxj:
                        try:
                            Neighbox = self.getBox(k, l)
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
                                            newMinesCandidates.append([i, j])
                                            self[i, j] = 1 #mine
                                        for coord in BmA:
                                            i = (coord - 1) // self.width  # 110 = row 10, column 10
                                            j = (coord - 1) % self.width + 1
                                            if self[i, j] == 0:
                                                determinable += 1
                                            removedMinesCandidates.append([i, j])
                                            self[i, j] = 2 #empty
                                        box.solved = True
                                        Neighbox.unknownSet = AaB # intersection
                                    # TODO compute the inverse operation here for optimization?

                        except IndexError:  # safety zone not big enough
                            pass

        return changed, determinable, newMinesCandidates, removedMinesCandidates

    def checkByTrying(self, listOfBoxes):
        pass


class GameStructures:
    def __init__(self, width, height, mines):
        self.freeBoxes = width * height

        self.width = width
        self.height = height

        self.matrix = []
        self.visibleMatrix = []
        self.determinable = 0
        self.uncovered = 0

        #self.generateDummy()
        self.generateMatrix(self.freeBoxes, width, height, mines)

        self.freeBoxes -= mines
        self.mines = mines

        self.virtualPlayer = VirtualPlayer(self.width, self.height)

    def load(self, matrix, visibleMatrix, VP, determinable, mines, width, height):
        self.matrix = matrix
        self.visibleMatrix = visibleMatrix
        self.determinable = determinable
        self.mines = mines
        self.width = width
        self.height = height

        self.virtualPlayer = VP

        #self.virtualPlayer.load(determinableList)

    def generateDummy(self):

        self.width = 5
        self.height = 2

        self.matrix = [[-5, -5, -5, -5, -5, -5, -5], [-5, -1, 1, 1, -1, 1, -5], [-5, 1, 1, 1, 1, 1, -5],
                       [-5, -5, -5, -5, -5, -5, -5]]

        self.visibleMatrix = [[0] * (self.width + 2) for _ in range(self.height + 2)]

    def generateMatrix(self, freeBoxes, width, height, mines):
        """
        Generate matrices and place mines.
        self.matrix has >-1 in empty boxes, -1 when mine is present, -5 in boundary boxes
        self.visibleMatrix has 0 when invisible, 1 when uncovered and 2 when flagged
        self.determinableMatrix has 0 when indeterminable, 1 when determinable mine, 2 when determinable blank box
        """

        matrix = [[1] * (width + 2) for _ in range(height + 2)]  # matrix has safety zone around
        visibleMatrix = [[0] * (width + 2) for _ in range(height + 2)]  # matrix has safety zone around
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

        for i in range(1, height + 1):
            for j in range(1, width + 1):
                if matrix[i][j] == -1:  # here is mine, add 1 to neighbours
                    self.changeNeighbourNumbers(i, j)

    def changeNeighbourNumbers(self, i, j, amount=1):
        matrix = self.matrix

        for k in range(-1, 2):
            matrix[i + 1][j + k] += self.increaseNeighbour(matrix, i + 1, j + k, amount)
        matrix[i][j - 1] += self.increaseNeighbour(matrix, i, j - 1, amount)
        matrix[i][j + 1] += self.increaseNeighbour(matrix, i, j + 1, amount)
        for k in range(-1, 2):
            matrix[i - 1][j + k] += self.increaseNeighbour(matrix, i - 1, j + k, amount)

    def increaseNeighbour(self, matrix, i, j, amount):
        if matrix[i][j] < 0:
            return 0
        else:
            return amount

    def calculateNeighbours(self, i, j):
        self.matrix[i][j] = 0
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                if self.matrix[k][l] == -1:
                    self.matrix[i][j] += 1

    def uncoverBox(self, i, j, flag=False):
        VP = self.virtualPlayer
        if flag:
            self.visibleMatrix[i][j] = 2
        elif self.visibleMatrix[i][j] == 1:
            print('You already uncovered this box.')
        else:
            self.freeBoxes -= 1

            if (self.determinable > 0 and VP[i, j] == 0) or VP[i, j] == 1:
                self.matrix[i][j] = -1
                return False  # You Lost

            if VP[i, j] == 2:
                self.determinable -= 1
            VP[i, j] = 2
            placeMine = False
            if self.matrix[i][j] == -1:  # we have to move this mine, because it was not determinable
                self.calculateNeighbours(i, j) #remove the mine and calculate the correct number
                self.moveMine(i, j)
                placeMine = True

            self.visibleMatrix[i][j] = 1

            knownMines, unknownSet = self.getUnknownSet(i, j)
            if self.checkUnknownSet(unknownSet, i, j):
                VP.setBox(i, j, Box(solved=False, unknownSet=unknownSet,
                                    modified=True, toSolve=self.matrix[i][j] - knownMines))
            if placeMine:
                pass

            if self.matrix[i][j] == 0:
                if self.uncoverWave(i, j):
                    VP.updateUnknownSets()
            newMinesCandidates, removedMinesCandidates = self.determinableWave()
            return True

    def getUnknownSet(self, i, j):
        VP = self.virtualPlayer
        # unknownSet = []
        unknownSet = set()
        knownMines = 0
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                if VP[k, l] == 0 and self.matrix[k][l] > -2:
                    # unknownSet.append([k,l])
                    unknownSet.add(k * self.width + l)
                elif VP[k, l] == 1:
                    knownMines += 1
        # print (knownMines, unknownSet)
        return knownMines, unknownSet

    def checkUnknownSet(self, unknownSet, i, j):
        """
        Check if we already know about this set, have to look in the 2 distance for equality.
        :param unknownSet: set of indices of unknown boxes surrounding a new box
        :param i: x index of new box
        :param j: y index of new box
        :return: True if this set is unknown else False
        """
        VP = self.virtualPlayer
        if not unknownSet:
            return False
        for k in range(i - 2, i + 3):
            for l in range(j - 2, j + 3):
                try:
                    box = VP.getBox(k, l)
                    if box and box.unknownSet == unknownSet:
                        return False
                except IndexError:  # safety zone not big enough
                    pass
        # print ('DIFFERENT', unknownSet)
        return True

    def uncoverWave(self, i, j):
        VP = self.virtualPlayer
        modified = False
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                if (self.visibleMatrix[k][l] == 0) and (self.matrix[k][l] > -1):
                    modified = True
                    if self.matrix[k][l] == 0:
                        self.visibleMatrix[k][l] = 1
                        if VP[k, l] == 2:
                            self.determinable -= 1
                        VP[k, l] = 2
                        self.freeBoxes -= 1
                        self.uncoverWave(k, l)
                    else:
                        self.visibleMatrix[k][l] = 1
                        if VP[k, l] == 2:
                            self.determinable -= 1
                        VP[k, l] = 2
                        self.freeBoxes -= 1
                        knownMines, unknownSet = self.getUnknownSet(k, l)
                        if self.checkUnknownSet(unknownSet, k, l):
                            VP.setBox(k, l, Box(solved=False, unknownSet=unknownSet,
                                                modified=True, toSolve=self.matrix[k][l] - knownMines))
        return modified

    def moveMine(self, fromX, fromY):
        try:
            newMinesCandidates, removedMinesCandidates = self.determinableWave()
            fixed = -1 #need to add one mine
            for mine in newMinesCandidates:
                i, j = mine
                if self.matrix[i][j] != -1:
                    fixed += 1
                    self.matrix[i][j] = -1
                    self.changeNeighbourNumbers(i, j)
                    # print('REAL CANDIDATE for mine', i, j)
            for mine in removedMinesCandidates:
                i, j = mine
                if self.matrix[i][j] == -1:
                    fixed -= 1
                    self.changeNeighbourNumbers(i, j, -1)
                    self.calculateNeighbours(i, j)
                    # print('REAL CANDIDATE for empty', i, j)

            if fixed == 0:
                raise doneException
            VP = self.virtualPlayer

            candidates = set()  # {(missingMines, [list of positions to place the mines]), ...}
            for i in range(1, self.height + 1):
                for j in range(1, self.width + 1):
                    if self.visibleMatrix[i][j] == 1 and self.matrix[i][j] > 0:  # number visible
                        box = VP.getBox(i, j)
                        if not box.solved:
                            candidates.add((box.toSolve, frozenset(box.unknownSet)))
            success, newMines = self.processCandidates(candidates)

            if newMines:
                placedMines = self.rearangeMines(newMines, candidates)
                if placedMines > 1:
                    self.removeMines(placedMines-1)
                raise doneException

            if not candidates:
                for i in range(1, self.height + 1):
                    for j in range(1, self.width + 1):
                        if VP[i, j] == 0 and self.matrix[i][j] > -1:
                            possibleCandidate = True
                            for k in range(i - 1, i + 2):
                                if not possibleCandidate:
                                    break
                                for l in range(j - 1, j + 2):
                                    if self.visibleMatrix[k][l] == 1 and self.matrix[k][l] > 0:  # number visible
                                        possibleCandidate = False
                                        break
                            if possibleCandidate:
                                candidates.add(i * self.width + j)
                                # print ('CANDIDATES', candidates)

            if not candidates:
                print('ERROR')
            else:
                self.placeMines([candidates.pop()])
        except doneException as e:
            # fix the original mine neighbours
            self.changeNeighbourNumbers(fromX, fromY, amount=-1)

    def rearangeMines(self, newMines, candidates):
        allCells = set()
        for candidate in candidates:
            mines, cells = candidate
            allCells.update(cells)

        placedMines = 0
        # print(newMines, allCells)
        for cell in allCells:
            cell -= 1  # 110 = row 10, column 10
            i = cell // self.width
            j = cell % self.width + 1

            if cell+1 in newMines:
                # print('NEWMINE', i, j)
                if self.matrix[i][j] != -1:
                    placedMines += 1
                    self.matrix[i][j] = -1
                    self.changeNeighbourNumbers(i, j)
            elif self.matrix[i][j] == -1:
                # print('REMOVEDMINE', i, j)
                placedMines -= 1
                self.changeNeighbourNumbers(i, j, -1)
                self.calculateNeighbours(i, j)
        return placedMines


    def placeMines(self, newMines):
        for newMine in newMines:
            newMine -= 1  # 110 = row 10, column 10
            i = newMine // self.width
            j = newMine % self.width + 1
            self.matrix[i][j] = -1
            self.changeNeighbourNumbers(i, j)

    def removeMines(self, number):
        if number == 0:
            return
        VP = self.virtualPlayer
        possibleCandidates = []
        # TODO improve - duplicite code for possibleCandidate
        for i in range(1, self.height + 1):
            for j in range(1, self.width + 1):
                if VP[i, j] == 0 and self.matrix[i][j] == -1:
                    possibleCandidate = True
                    for k in range(i - 1, i + 2):
                        if not possibleCandidate:
                            break
                        for l in range(j - 1, j + 2):
                            if self.visibleMatrix[k][l] == 1 and self.matrix[k][l] > 0:  # number visible, not mine
                                possibleCandidate = False
                                break
                    if possibleCandidate:
                        possibleCandidates.append([i, j])

        newMines = sample(range(len(possibleCandidates)), number)
        for newMine in newMines:
            i, j = possibleCandidates[newMine]
            self.matrix[i][j] = 0
            self.changeNeighbourNumbers(i, j, amount=-1)
            self.calculateNeighbours(i, j)

    def determinableWave(self):
        newMinesCandidates, newMines = [], []
        removedMinesCandidates, removedMines = [], []
        VP = self.virtualPlayer
        VP.updateUnknownSets()
        changed = True
        while changed:
            # print('determinableWave')
            changed = False
            for i in range(1, self.height + 1):
                for j in range(1, self.width + 1):
                    if self.visibleMatrix[i][j] == 1:
                        box = VP.getBox(i, j)
                        if box and box.modified and not box.solved:
                            # print (i,j)
                            newChange, determinable, newMines, removedMines = VP.processBox(box, i, j)
                            changed += newChange
                            self.determinable += determinable
                            newMinesCandidates += newMines
                            removedMinesCandidates += removedMines
            VP.updateUnknownSets()
        return newMinesCandidates, removedMinesCandidates

    def processCandidates(self, candidates):
        # TODO improve the recursion, do not check all possiblities
        # TODO add randomness - now the first result gets chosen
        # print('PROCESS', candidates)
        minesToPlace = set()

        minePlaced = False
        possible = True
        totalMines = 0

        for candidate in candidates:
            mines, cells = candidate
            totalMines += mines
            if len(cells) == mines:
                minePlaced = True
                minesToPlace.update(cells)

        if totalMines == 0:
            return True, []

        if not minePlaced:
            for candidate in candidates:
                mines, cells = candidate
                if mines <= 0:
                    continue
                for cell in cells:
                    minesToPlace.add(cell)
                    newPossible, newCandidates = self.getCandidates(candidates, minesToPlace)
                    if newPossible and newCandidates:
                        # print('Added cell', cell)
                        possible, newCandidates = self.processCandidates(newCandidates)
                        if possible:
                            minesToPlace.update(newCandidates)
                            # print('NEW CELL', cell, possible)
                            return possible, minesToPlace
                    minesToPlace.remove(cell)
        else: #some easy placing
            newPossible, newCandidates = self.getCandidates(candidates, minesToPlace)
            if newPossible and newCandidates:
                minePlaced = True
                possible, newCandidates = self.processCandidates(newCandidates)
            minesToPlace.update(newCandidates)
        if minePlaced:
            return possible, minesToPlace
        return False, []

    def getCandidates(self, candidates, minesToPlace):
        newCandidates = set()
        possible = True

        for candidate in candidates:
            mines, cells = candidate
            newMines = mines - len(cells.intersection(minesToPlace))
            if newMines < 0:
                possible = False
                return possible, []
            newCandidates.add((newMines, frozenset(cells-minesToPlace)))
        return possible, newCandidates
