import pyqtgraph as pg
from PyQt5 import QtGui, QtCore


pg.setConfigOption("crashWarning", True)


class VisualGraphs:

    def __init__(self):
        self.app = QtGui.QApplication([])
        self.mainWindow = QtGui.QMainWindow()
        self.mainWindow.setWindowTitle("EvoSim")
        self.mainWindow.resize(800, 800)

        self.centralWidget = QtGui.QWidget()
        self.mainWindow.setCentralWidget(self.centralWidget)
        self.layout = QtGui.QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.plots = {}
        self.updateTimerTime = 0

    def AddPlot(self, name, leftLabel, bottomLabel):
        plotData = [None, None]

        plotData[0] = pg.PlotWidget(name=name)
        plotData[0].setLabel("left", leftLabel)
        plotData[0].setLabel("bottom", bottomLabel)

        plotData[1] = plotData[0].plot()
        plotData[1].setPen((255, 255, 255))

        self.layout.addWidget(plotData[0])
        self.plots[name] = plotData

    def SetUpdateFunction(self, updateFunc, updateTime):
        self.updateTimer = QtCore.QTimer()
        self.updateTimer.timeout.connect(updateFunc)
        self.updateTimerTime = updateTime

    def StartProgram(self):
        self.mainWindow.show()

        self.updateTimer.start(self.updateTimerTime)

        QtGui.QApplication.instance().exec_()


class Simulation:

    def __init__(self, worldSizeX = 100, worldSizeY = 100):
        self.data = {
            "population": []
        }

        self.world = []

        self.sizeX = worldSizeX
        self.sizeY = worldSizeY

        for _ in range(0, worldSizeX):
            rowData = []
            for _ in range(0, worldSizeY):
                rowData.append({})
            self.world.append(rowData)

        self.step = 0

        self.objects = {}

        self.customData = SimCustomData()

    def RegisterNewObject(self, type):
        for xStrip in self.world:
            for tile in xStrip:
                tile[type] = []

        self.objects[type] = []

    def AddNewObject(self, object):
        self.world[object.x][object.y][object.type].append(object)
        self.objects[object.type].append(object)

    def RemoveObject(self, object):
        self.world[object.x][object.y][object.type].remove(object)
        self.objects[object.type].remove(object)

    def MoveObject(self, object, x, y):
        self.world[object.x][object.y][object.type].remove(object)
        self.world[x][y][object.type].append(object)


class SimCustomData:
    """used as an easy way to add custom data to the sim"""


class BaseObject:

    def __init__(self, parentSim):
        self.simulation = parentSim

        self.x = 0
        self.y = 0
        self.type = "null"

    def SetPosition(self, newX, newY):
        self.simulation.MoveObject(self, newX, newY)
        self.x = newX
        self.y = newY
