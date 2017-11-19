from PyQt5 import QtCore, QtGui, QtWidgets
from numpy import genfromtxt, ndarray
import sys
import os
import DataStructures
import pickle
import time


class GameField(QtWidgets.QWidget):
    class ModifiedButton(QtWidgets.QPushButton):
        def __init__(self, gameField, *args, **kwargs):
            super(QtWidgets.QPushButton, self).__init__(*args, **kwargs)
            self.gameField = gameField

        def mousePressEvent(self, QMouseEvent):
            self.setText('{}'.format(self.gameField.gameStructure.determinable))
            self.gameField.s += 2

        def mouseReleaseEvent(self, QMouseEvent):
            self.setText('Number of uncoverable boxes')

    def __init__(self, parent, app):
        super(GameField, self).__init__(parent)
        self.parent = parent
        self.app = app

        self.moves = 0
        self.messy = False

        self.width = 30
        self.height = 20
        self.mines = 70
        self.remainingMines = 0

        # Time counters #
        self.s = 0
        self.m = 0
        self.h = 0
        self.timeSpeed = 1

        gameStructure = DataStructures.GameStructures(self.width, self.height, self.mines)
        self.gameStructure = gameStructure
        self.dataList = gameStructure.matrix
        self.visibleList = gameStructure.visibleMatrix
        self.VP = gameStructure.virtualPlayer

        self.setWindowTitle("Fair minesweeper")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.setSizePolicy(sizePolicy)

        self.initiateWidgets()

        self.loadTopResults()

    def initiateWidgets(self):
        self.tableView = QtWidgets.QTableView()

        font = QtGui.QFont("Helvetica", 14)
        self.tableView.setFont(font)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.initiateGameField()

        # custom right and left click events
        self.tableView.clicked.connect(self.onClick)
        self.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.onClick)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.tableView, stretch=100)

        rightLayout = QtWidgets.QVBoxLayout()

        # ------------Remaining mines widget ------------#
        remainingLayout = QtWidgets.QHBoxLayout()
        labelRemaining = QtWidgets.QLabel('Remaining mines:')
        labelRemaining.setFont(font)
        self.remaining = QtWidgets.QLabel(str(self.mines))
        self.remaining.setFont(font)
        remainingLayout.addWidget(labelRemaining)
        remainingLayout.addWidget(self.remaining)
        rightLayout.addLayout(remainingLayout)

        # -----------Possible to determine -----------------#
        self.buttonUncoverable = self.ModifiedButton(self, 'Number of uncoverable boxes')
        rightLayout.addWidget(self.buttonUncoverable)

        self.buttonPossible = QtWidgets.QPushButton('Show determinable boxes')
        rightLayout.addWidget(self.buttonPossible)
        self.buttonPossible.pressed.connect(self.hint)

        # ------------Time widget ------------#
        self.s, self.m, self.h = 0, 0, 0

        self.lcd = QtWidgets.QLCDNumber(self)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.time)
        self.startTiming()
        rightLayout.addWidget(self.lcd)

        # ------------Save and load widgets -------#
        saveButton = QtWidgets.QPushButton('Save')
        saveButton.pressed.connect(self.save)
        rightLayout.addWidget(saveButton)
        loadButton = QtWidgets.QPushButton('Load')
        loadButton.pressed.connect(self.load)
        rightLayout.addWidget(loadButton)

        # ------------Save and load widgets -------#
        saveButton = QtWidgets.QPushButton('SaveDummy')
        saveButton.pressed.connect(self.saveDummy)
        #rightLayout.addWidget(saveButton)
        loadButton = QtWidgets.QPushButton('LoadDummy')
        loadButton.pressed.connect(self.loadDummy)
        #rightLayout.addWidget(loadButton)

        # ------------New game widget ------------#
        label = QtWidgets.QLabel('Set field size')
        label.setFont(font)
        self.rowsWidget = QtWidgets.QLineEdit()
        self.rowsWidget.setValidator(QtGui.QIntValidator())
        self.rowsWidget.setMaxLength(2)
        self.rowsWidget.setFixedWidth(26)
        self.rowsWidget.setFont(font)
        self.rowsWidget.setText(str(self.height))
        labelx = QtWidgets.QLabel(' x ')
        labelx.setFont(font)
        self.columnsWidget = QtWidgets.QLineEdit()
        self.columnsWidget.setValidator(QtGui.QIntValidator())
        self.columnsWidget.setMaxLength(2)
        self.columnsWidget.setFixedWidth(26)
        self.columnsWidget.setFont(font)
        self.columnsWidget.setText(str(self.width))
        sizesLayout = QtWidgets.QHBoxLayout()
        sizesLayout.addWidget(label)
        sizesLayout.addWidget(self.rowsWidget)
        sizesLayout.addWidget(labelx)
        sizesLayout.addWidget(self.columnsWidget)
        rightLayout.addLayout(sizesLayout)

        labelMines = QtWidgets.QLabel('Set mines number')
        labelMines.setFont(font)
        self.minesWidget = QtWidgets.QLineEdit()
        self.minesWidget.setValidator(QtGui.QIntValidator())
        self.minesWidget.setMaxLength(3)
        self.minesWidget.setFixedWidth(40)
        self.minesWidget.setFont(font)
        self.minesWidget.setText(str(self.mines))
        minesLayout = QtWidgets.QHBoxLayout()
        minesLayout.addWidget(labelMines)
        minesLayout.addWidget(self.minesWidget)
        rightLayout.addLayout(minesLayout)

        self.startButton = QtWidgets.QPushButton('Start', self)
        self.startButton.clicked.connect(self.start)
        rightLayout.addWidget(self.startButton)
        layout.addLayout(rightLayout)

        self.adjustSize()
        self.app.processEvents()
        self.parent.adjustSize()  # TODO should be called later to correctly resize
        # self.parent.adjustSize()

    def initiateGameField(self):
        self.messy = False
        self.tableModel = MyTableModel(self, self.visibleList, self.dataList, self.VP)
        self.tableView.setModel(self.tableModel)

        for i in range(len(self.visibleList[0])):
            self.tableView.setColumnWidth(i, 30)
        self.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableView.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # x, y = self.tableView.sizeHint().width(), self.tableView.sizeHint().height()
        # print (self.width,self.height)
        # Rewrite sizeHint function to return modified values?
        # self.parent.resize()

        self.parent.setFixedSize((self.width + 1) * 30 + 225,
                                 (self.height + 1) * 30 + 18)  # needed e.g. for making the field smaller
        # self.parent.setFixedSize(x + 225, y + 18)
        # self.parent.setFixedSize(x + 50, y + 18)

        self.parent.adjustSize()  # TODO should be called later to correctly resize
        # self.tableView.updateGeometry()

    def time(self):
        if self.s < 60 - self.timeSpeed:
            self.s += self.timeSpeed
        else:
            if self.m < 59:
                self.s -= 60 - self.timeSpeed
                self.m += 1
            elif self.m == 59 and self.h < 24:
                self.h += 1
                self.m -= 59
                self.s -= 60 - self.timeSpeed
            else:
                self.timer.stop()

        time = "{0}:{1}:{2}".format(self.h, '0' * (2 - len(str(self.m))) + str(self.m),
                                    '0' * (2 - len(str(self.s))) + str(self.s))

        self.lcd.setDigitCount(len(time))
        self.lcd.display(time)

    def resetTiming(self):
        self.h = self.m = self.s = 0
        time = "{0}:{1}:{2}".format(self.h, '0' + str(self.m), '0' + str(self.s))

        self.lcd.setDigitCount(len(time))
        self.lcd.display(time)

    def startTiming(self):
        self.timer.start(1000)

    def hint(self):
        if self.gameStructure.determinable == 0:
            return
        turnOff = self.tableModel.showDeterminable
        self.tableModel.showDeterminable = False if turnOff else True
        self.timeSpeed = 1 if turnOff else 3
        if turnOff:
            self.buttonPossible.setText('Show determinable boxes')
        else:
            self.buttonPossible.setText('Hide determinable boxes')
        self.s += 0 if turnOff else 3
        self.tableModel.update()

    def loadTopResults(self):
        self.topResults = {}
        if os.path.isfile('topScores.FMSr'):
            try:
                file = genfromtxt('topScores.FMSr', dtype=str)
                if type(file[0]) is not ndarray:  # different behaviour of genfromtxt with only one line of data
                    file = [file]
                for line in enumerate(file):
                    line = line[1]  # line = (index, (width, height, ... ))
                    self.topResults[line[0] + ':' + line[1] + ':' + line[2]] = (
                        ((int(line[3]) * 60) + int(line[4])) * 60 + int(line[5]), line[6])  # total time spent, name
            except:
                pass
                # QtWidgets.QMessageBox.warning(self, "Load failure",
                #                               "Could not load top scores from file topScores.FMSr.",
                #                               QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)

    def saveTopResults(self):
        with open('topScores.FMSr', 'w') as outfile:
            outfile.write('#Width  Height  Mines  Hours  Minutes  Seconds  Name\n')
            for key in sorted(self.topResults.keys(), key=lambda k: tuple(map(int, k.split(':')))):
                value, name = self.topResults[key]
                s, rest = value % 60, value // 60
                m, h = rest % 60, rest // 60  # get time
                key = key.replace(':', '\t') + '\t'
                outfile.write(key + '\t'.join((str(h), str(m), str(s))) + '\t' + name + '\n')

    def save(self):
        # Data matrix visible matrix total mines field width  field height   remaining mines   hours, minutes, seconds
        pickle.dump((
            self.dataList, self.visibleList, self.VP, self.mines, self.width, self.height,
            self.remaining.text(), self.gameStructure.determinable, self.h, self.m, self.s),
            open('savedPosition.FMS', 'wb'))
        self.messy = False

    def saveDummy(self):
        # Data matrix visible matrix total mines field width  field height   remaining mines   hours, minutes, seconds
        pickle.dump((
            self.dataList, self.visibleList, self.mines, self.width, self.height, self.remaining.text(), self.h,
            self.m, self.s), open('savedPositionDummy.FMS', 'wb'))
        self.messy = False

    def load(self):
        # TODO FIX load and save to work with smart functionality
        dataList, visibleList = [], []
        if os.path.isfile('savedPosition.FMS'):
            (dataList, visibleList, VP, self.mines, self.width, self.height, self.remainingMines,
             determinable, self.h, self.m, self.s) = pickle.load(open('savedPosition.FMS', 'rb'))
            self.rowsWidget.setText(str(self.height))
            self.columnsWidget.setText(str(self.width))
            self.minesWidget.setText(str(self.mines))
        else:
            return
        self.gameStructure.load(dataList, visibleList, VP, determinable, self.mines,
                                self.width, self.height)
        self.start(load=True)
        self.messy = False

    def loadDummy(self):
        dataList, visibleList = [], []
        if os.path.isfile('savedPositionDummy.FMS'):
            (dataList, visibleList, self.mines, self.width, self.height, self.remainingMines, self.h, self.m,
             self.s) = pickle.load(open('savedPositionDummy.FMS', 'rb'))
            self.rowsWidget.setText(str(self.height))
            self.columnsWidget.setText(str(self.width))
            self.minesWidget.setText(str(self.mines))

        visibleList = [[0] * (self.width + 2) for _ in range(self.height + 2)]

        self.gameStructure.load(dataList, visibleList, [[0] * (self.width + 2) for _ in range(self.height + 2)], 0,
                                self.mines, self.width, self.height)
        self.start(load=True)
        self.messy = False

    def start(self, load=False):
        try:
            self.width, self.height = int(self.columnsWidget.text()), int(self.rowsWidget.text())
            self.mines = int(self.minesWidget.text())
            if self.width > 50 or self.height > 30:
                QtWidgets.QMessageBox.warning(self, "Too big field",
                                              "Cannot set width > 50 or height > 30.",
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)
                return
            if self.mines >= self.width * self.height:
                QtWidgets.QMessageBox.warning(self, "Too many mines",
                                              "Cannot set mines >= width*height.",
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)
                return
            else:
                self.moves = 0

                if not load:
                    gameStructure = DataStructures.GameStructures(self.width, self.height, self.mines)
                    self.gameStructure = gameStructure
                    self.remaining.setText(str(self.mines))
                    self.resetTiming()
                else:
                    self.remaining.setText(self.remainingMines)
                self.dataList = self.gameStructure.matrix
                self.visibleList = self.gameStructure.visibleMatrix
                self.VP = self.gameStructure.virtualPlayer
                self.initiateGameField()

        except Exception as e:
            print(e)
            print('Cannot set given field dimension.')

    def onClick(self, index):
        # print ('tableView.onClick:', index)

        try:  # Left Click
            row, column = index.row() + 1, index.column() + 1  # safety zone
            visibleListItem = self.visibleList[row][column]

            if visibleListItem < 0:
                QtWidgets.QMessageBox.information(self, "Marked as flag",
                                                  'This box is already marked as flag. Unmark it first.',
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)
            elif visibleListItem == 0:
                self.messy = True  # unsaved change

                self.moves += 1

                if not self.gameStructure.uncoverBox(row, column):  # You LOST
                    QtWidgets.QMessageBox.critical(self, "You lost",
                                                   "Sorry, you lost.",
                                                   QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)

                uncovered = 0
                for i in range(len(self.visibleList)):
                    for j in range(len(self.visibleList[0])):
                        # TODO improve
                        uncovered += 1 if self.visibleList[i][j] == 1 and \
                                          self.dataList[i][j] >= 0 else 0  # Don't count uncovered mines
                        index = self.tableView.model().index(i, j)
                        # TODO HotFix
                        self.tableModel.dataChanged.emit(index, index)

                if uncovered + self.mines == self.width * self.height:
                    self.gameWon()

                self.tableModel.dataChanged.emit(index, index)

        except AttributeError:  # Right Click
            index = self.tableView.indexAt(index)
            row, column = index.row() + 1, index.column() + 1  # safety zone
            visibleListItem = self.visibleList[row][column]
            # print (visibleListItem)
            if visibleListItem <= 0:  # Not uncovered yet
                self.messy = True  # unsaved change

                self.visibleList[row][column] = -(visibleListItem + 1)  # 0 to -1 and vice versa
                addedFlag = 1 if visibleListItem == 0 else -1
                remainingFlags = int(self.remaining.text()) - addedFlag
                self.remaining.setText(str(remainingFlags))
                if self.checkFlagWinCondition(remainingFlags):
                    self.gameWon()
                self.tableModel.dataChanged.emit(index, index)
                # print(visibleListItem)

    def checkFlagWinCondition(self, remainingFlags):
        if remainingFlags != 0:
            return False
        for row in range(self.height):
            for column in range(self.width):
                if self.visibleList[row][column] == -1 and self.dataList[row][column] != -1:  # Not a mine is flagged
                    return False
        return True

    def gameWon(self):
        self.messy = False
        key = str(self.width) + ':' + str(self.height) + ':' + str(self.mines)
        previousTop, previousName = self.topResults.get(key, (-1, ''))
        newTime = ((self.h * 60) + self.m) * 60 + self.s
        if newTime < previousTop or previousTop == -1:
            QtWidgets.QMessageBox.information(self, "You won",
                                              'Hooray! You won! \nTotal time spent: {0}:{1}:{2}.'.format(
                                                  self.h, '0' * (2 - len(str(self.m))) + str(self.m),
                                                          '0' * (2 - len(str(self.s))) + str(self.s)),
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)
            dialog = NewRecordDialog(self.width, self.height, self.mines, previousTop - newTime, previousName)
            name = 'Unknown'
            if dialog.exec_():
                name = dialog.lineEdit.text()
            self.topResults[key] = (newTime, name)
        else:
            QtWidgets.QMessageBox.information(self, "You won",
                                              'Hooray! You won! Total time spent: {0}:{1}:{2}.\n Nevertheless, {3} managed to solve this {4} seconds faster.'.format(
                                                  self.h, '0' * (2 - len(str(self.m))) + str(self.m),
                                                          '0' * (2 - len(str(self.s))) + str(self.s), previousName,
                                                          newTime - previousTop),
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)


class NewRecordDialog(QtWidgets.QDialog):
    def __init__(self, width, height, mines, wonBySeconds, previousName, parent=None):
        super(NewRecordDialog, self).__init__(parent)

        mainLayout = QtWidgets.QVBoxLayout()

        if wonBySeconds < 0:  # First record ever:
            label = 'You set a new record for the field {}x{} with {} mines.'.format(
                width, height, mines)
        else:
            label = 'You set a new record for the field {}x{} with {} mines.\nYou have beaten {} by {} seconds'.format(
                width, height, mines, previousName, wonBySeconds)
        mainLayout.addWidget(QtWidgets.QLabel(label))

        layout = QtWidgets.QHBoxLayout()

        layout.addWidget(QtWidgets.QLabel('Your name:'))
        self.lineEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.lineEdit)

        self.acceptButton = QtWidgets.QPushButton('Save')
        self.acceptButton.pressed.connect(super(NewRecordDialog, self).accept)
        layout.addWidget(self.acceptButton)

        mainLayout.addLayout(layout)
        self.setLayout(mainLayout)


class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, visibleList, dataList, VP):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.visibleList = visibleList
        self.VP = VP
        self.dataList = dataList
        self.colors = [QtGui.QColor("#808080"), QtGui.QColor("#FFFFFF"), QtGui.QColor("#000000"),
                       QtGui.QColor("#FF0000")]
        self.showDeterminable = False

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

    def rowCount(self, parent, **kwargs):
        return len(self.visibleList) - 2  # minus safety zone

    def columnCount(self, parent, **kwargs):
        return len(self.visibleList[0]) - 2  # minus safety zone

    def data(self, index, role):
        row, column = index.row() + 1, index.column() + 1  # safety zone
        value = self.visibleList[row][column]
        if not index.isValid():
            return None
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        elif role == QtCore.Qt.BackgroundRole:
            if value == 1:  # Visible
                value = self.dataList[row][column]
                if value == -1:
                    return QtGui.QBrush(QtGui.QColor(255, 0, 0, 255))
                else:
                    return QtGui.QBrush(QtGui.QColor(255, 0, 0, 25 * value))
            elif value == 0:
                if self.showDeterminable:
                    if self.VP[row, column] == 1:
                        #return QtGui.QBrush(QtGui.QColor(255, 215, 0, 100))
                        return QtGui.QBrush(QtGui.QColor(0, 0, 0, 100))
                    elif self.VP[row, column] == 2:
                        return QtGui.QBrush(QtGui.QColor(0, 0, 0, 100))
                        # QtGui.QColor(QtCore.Qt.black)
                return QtGui.QBrush(QtGui.QColor(30, 30, 30, 30))
            else:
                return QtGui.QBrush(QtGui.QColor(0, 0, 200, 100))
        elif role == QtCore.Qt.DisplayRole:
            if value == 1:
                value = self.dataList[row][column]
                if value == -1:
                    value = 'X'
                elif value == 0:
                    return ' '
                return value
            elif value == 0:
                return None
            else:
                return 'P'

    def update(self):
        self.layoutAboutToBeChanged.emit()
        self.layoutChanged.emit()


class Main(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

    def closeEvent(self, event):
        if self.gameField.messy is False:
            main.gameField.saveTopResults()
            return

        saveQuestion = QtWidgets.QMessageBox()
        saveQuestion.setText('Do you want to save current progress?')
        saveQuestion.addButton(QtWidgets.QPushButton('Yes'), QtWidgets.QMessageBox.YesRole)
        saveQuestion.addButton(QtWidgets.QPushButton('No'), QtWidgets.QMessageBox.NoRole)
        saveQuestion.addButton(QtWidgets.QPushButton('Cancel'), QtWidgets.QMessageBox.RejectRole)
        reply = saveQuestion.exec_()

        if reply == 0:  # YES
            main.gameField.saveTopResults()
            main.gameField.save()
            event.accept()
        elif reply == 1:  # NO
            main.gameField.saveTopResults()
            event.accept()
        else:  # CANCEL
            event.ignore()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()

    main.gameField = GameField(main, app)
    main.setCentralWidget(main.gameField)
    main.show()

    sys.exit(app.exec_())
