import pyqtgraph as pg
from PyQt5 import QtGui, QtCore
import random


pg_app = QtGui.QApplication([])
app_mainWindow = QtGui.QMainWindow()
app_mainWindow.setWindowTitle("EvoSim")
app_mainWindow.resize(800, 800)
app_centralWidget = QtGui.QWidget()
app_mainWindow.setCentralWidget(app_centralWidget)
app_layout = QtGui.QVBoxLayout()
app_centralWidget.setLayout(app_layout)

app_plotWidget1 = pg.PlotWidget(name="Plot1")
app_layout.addWidget(app_plotWidget1)

app_mainWindow.show()

graph_Population = app_plotWidget1.plot()
graph_Population.setPen((200, 200, 100))

app_plotWidget1.setLabel("left", "Population")
app_plotWidget1.setLabel("bottom", "Day")


data_population = []
step = 1

sim_roomSizeX = 100
sim_roomSizeY = 100
sim_creatures = []

class creature():

    x = 0
    y = 0
    maxEnergy = 500
    energy = 0
    food = 0

    def startDay(self):
        choice = random.randrange(0, 4)

        if choice == 0:
            y = sim_roomSizeY
            x = random.randrange(0, sim_roomSizeX+1)
        elif choice == 1:
            x = sim_roomSizeX
            y = random.randrange(0, sim_roomSizeY+1)
        elif choice == 2:
            y = 0
            x = random.randrange(0, sim_roomSizeX+1)
        else:
            x = 0
            y = random.randrange(0, sim_roomSizeY+1)

        self.energy = self.maxEnergy
        self.food = 0

    def doStep(self):
        if self.energy > 0 and self.food < 2:
            while True:
                choice = random.randrange(0, 8)

                if choice == 0:
                    if self.y < sim_roomSizeY:
                        self.y += 1
                        break
                    else:
                        continue
                elif choice == 1:
                    if self.y < sim_roomSizeY and self.x < sim_roomSizeX:
                        self.y += 1
                        self.x += 1
                        break
                    else:
                        continue
                elif choice == 2:
                    if self.x < sim_roomSizeX:
                        self.x += 1
                        break
                    else:
                        continue
                elif choice == 3:
                    if self.y > 0 and self.x < sim_roomSizeX:
                        self.y -= 1
                        self.x += 1
                        break
                    else:
                        continue
                elif choice == 4:
                    if self.y > 0:
                        self.y -= 1
                        break
                    else:
                        continue
                elif choice == 5:
                    if self.y > 0 and self.x > 0:
                        self.y -= 1
                        self.x -= 1
                        break
                    else:
                        continue
                elif choice == 6:
                    if self.x > 0:
                        self.x -= 1
                        break
                    else:
                        continue
                elif choice == 7:
                    if self.y < sim_roomSizeY and self.x > 0:
                        self.y += 1
                        self.x -= 1
                        break
                    else:
                        continue

                print("ERROR: CREATURE DIDN'T MOVE.")
                print("CHOICE: " + str(choice))
                break

            self.energy -= 1

            index = 0
            indexToRemove = -1
            for itemFood in sim_food:
                if itemFood.x == self.x and itemFood.y == self.y:
                    indexToRemove = index
                    self.food += 1
                    break
                index += 1

            if indexToRemove > -1:
                sim_food.pop(indexToRemove)

            return True

        return False

    def evaluateDay(self):
        if self.food == 0:
            return [0]
        elif self.food == 1:
            return [1]
        else:
            return [2, creature()]


sim_food = []
sim_dailyFoodAmount = 30

class food():

    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


sim_startingPopulation = 5

data_population.append(sim_startingPopulation)
for _ in range(0, sim_startingPopulation):
    sim_creatures.append(creature())


def day():
    global sim_creatures

    for _ in range(0, sim_dailyFoodAmount):
        sim_food.append(food(random.randrange(1, sim_roomSizeX), random.randrange(1, sim_roomSizeY)))

    for singleCreature in sim_creatures:
        singleCreature.startDay()

    creatureMoved = False
    while True:
        for singleCreature in sim_creatures:
            moved = singleCreature.doStep()
            if not creatureMoved:
                creatureMoved = moved
        if not creatureMoved:
            break

        creatureMoved = False

    creaturesSurvived = []
    for singleCreature in sim_creatures:
        status = singleCreature.evaluateDay()
        if status[0] == 1:
            creaturesSurvived.append(singleCreature)
        elif status[0] == 2:
            creaturesSurvived.append(singleCreature)
            creaturesSurvived.append(status[1])

    sim_creatures = creaturesSurvived


def update():
    global step

    day()

    data_population.append(len(sim_creatures))

    graph_Population.setData(data_population[:step])
    step += 1

updateTimer = QtCore.QTimer()
updateTimer.timeout.connect(update)
updateTimer.start(1000)


QtGui.QApplication.instance().exec_()
