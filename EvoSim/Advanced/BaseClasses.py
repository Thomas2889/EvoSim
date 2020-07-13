import pyqtgraph as pg
from PyQt5 import QtGui, QtCore
import math


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

    def __init__(self, worldCellCount = 100, cellSize = 5):
        self.data = {
            "population": []
        }

        self.world = []

        self.size = worldCellCount * cellSize
        self.cellCount = worldCellCount
        self.cellSize = cellSize

        for x in range(0, worldCellCount):
            rowData = []
            for y in range(0, worldCellCount):
                rowData.append({})
            self.world.append(rowData)

        self.step = 0

        self.objects = {}

        self.customData = SimCustomData()

    def GetArea(self, x, y):
        return Vector2(math.floor(x / self.cellSize), math.floor(y / self.cellSize))

    def GetAngle(self, origin, taget):
        angle = math.atan2(taget.y, taget.x * -1) - math.atan2(origin.y, origin.x * -1)
        angle = angle * 180 / math.pi - 90
        if angle < 0:
            angle = angle + 360
        return angle

    def RegisterNewObject(self, type):
        for xStrip in self.world:
            for area in xStrip:
                area[type] = []

        self.objects[type] = []

    def AddNewObject(self, object):
        objectArea = self.GetArea(object.pos.x, object.pos.y)
        self.world[objectArea.x][objectArea.y][object.type].append(object)
        self.objects[object.type].append(object)

    def RemoveObject(self, object):
        objectArea = self.GetArea(object.pos.x, object.pos.y)
        self.world[objectArea.x][objectArea.y][object.type].remove(object)
        self.objects[object.type].remove(object)

    def MoveObject(self, object, x, y):
        objectArea = self.GetArea(object.pos.x, object.pos.y)
        newArea = self.GetArea(x, y)
        self.world[objectArea.x][objectArea.y][object.type].remove(object)
        self.world[newArea.x][newArea.y][object.type].append(object)


class SimCustomData:
    """used as an easy way to add custom data to the sim"""


class BaseObject:

    def __init__(self, parentSim):
        self.simulation = parentSim

        self.pos = Vector2()
        self.type = "null"

    def SetPosition(self, newX, newY):
        self.simulation.MoveObject(self, newX, newY)
        self.pos = Vector2(newX, newY)


class Vector2:

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y

    def ConstructFromAngle(self, angle, magnitude = 1):
        self.x = math.cos(angle) * magnitude
        self.y = math.sin(angle) * magnitude

    def Magnitude(self):
        return math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))
