import random, queue, threading, time

import BaseClasses as Base


class Creature(Base.BaseObject):

    def __init__(self, parentSim, maxEnergy):
        super().__init__(parentSim)

        self.type = "creature"

        self.food = 0
        self.energy = 0

        self.maxEnergy = maxEnergy
        self.angle = 0
        self.canStep = True

        self.reach = 1
        self.speed = 1

    def StartDay(self):
        choice = random.randrange(0, 4)

        choices = [
            {
                "y": self.simulation.size - 1,
                "x": random.randrange(0, self.simulation.size)
            },
            {
                "y": random.randrange(0, self.simulation.size),
                "x": self.simulation.size - 1
            },
            {
                "y": 0,
                "x": random.randrange(0, self.simulation.size)
            },
            {
                "y": random.randrange(0, self.simulation.size),
                "x": 0
            }
        ]

        self.SetPosition(choices[choice]["x"], choices[choice]["y"])
        self.angle = self.simulation.GetAngle(self.pos, Base.Vector2(self.simulation.size/2, self.simulation.size/2))
        self.energy = self.maxEnergy
        self.food = 0
        self.canStep = True

    def DoStep(self):
        if self.energy > 0 and self.food < 2:
            angleDelta = random.uniform(-10, 10)

            newAngle = self.angle + angleDelta
            moveVector = Base.Vector2()
            moveVector.ConstructFromAngle(newAngle, self.speed)
            newPos = self.pos + moveVector

            if not (0 < newPos.x < self.simulation.size and 0 < newPos.y < self.simulation.size):

                def line(vec1, vec2):
                    A = (vec1.y - vec2.y)
                    B = (vec2.x - vec1.x)
                    C = vec1.x*vec2.y - vec2.x*vec1.y
                    return A, B, -C

                def intersection(vec1, vec2, vec3, vec4):
                    L1 = line(vec1, vec2)
                    L2 = line(vec3, vec4)

                    D = L1[0] * L2[1] - L1[1] * L2[0]
                    Dx = L1[2] * L2[1] - L1[1] * L2[2]
                    Dy = L1[0] * L2[2] - L1[2] * L2[0]
                    if D != 0:
                        x = Dx / D
                        y = Dy / D
                        return Base.Vector2(x, y)
                    else:
                        return Base.Vector2()

                simSize = self.simulation.size-1
                walls = [
                    [Base.Vector2(0, simSize), Base.Vector2(simSize, simSize)],
                    [Base.Vector2(simSize, simSize), Base.Vector2(simSize, 0)],
                    [Base.Vector2(simSize, 0), Base.Vector2(0, 0)],
                    [Base.Vector2(0, 0), Base.Vector2(0, simSize)]
                ]
                wallsToUse = []

                if newPos.x < 0:
                    wallsToUse.append(3)
                else:
                    wallsToUse.append(1)

                if newPos.y < 0:
                    wallsToUse.append(2)
                else:
                    wallsToUse.append(0)

                inBoundaryX = 0
                inBoundaryY = 0
                found = False
                for wall in wallsToUse:
                    intersectionPoint = intersection(self.pos, newPos, walls[wall][0], walls[wall][1])

                    if 0 < intersectionPoint.x < self.simulation.size and 0 < intersectionPoint.y < self.simulation.size:
                        newPos = intersectionPoint
                        found = True
                        break
                    elif 0 < intersectionPoint.x < self.simulation.size:
                        inBoundaryX = intersectionPoint.x
                    else:
                        inBoundaryY = intersectionPoint.y

                if not found:
                    newPos.x = inBoundaryX
                    newPos.y = inBoundaryY

            self.SetPosition(newPos.x, newPos.y)
            self.angle = newAngle
            self.energy -= 1

            cellPos = self.simulation.GetArea(self.pos.x, self.pos.y)

            xRange = [cellPos.x-1, cellPos.x+2]
            yRange = [cellPos.y-1, cellPos.y+2]

            if cellPos.x == 0:
                xRange[0] = cellPos.x
            elif cellPos.x == self.simulation.cellCount-1:
                xRange[1] = cellPos.x+1

            if cellPos.y == 0:
                yRange[0] = cellPos.y
            elif cellPos.y == self.simulation.cellCount-1:
                yRange[1] = cellPos.y+1

            for cellX in range(xRange[0], xRange[1]):
                for cellY in range(yRange[0], yRange[1]):
                    for food in self.simulation.world[cellX][cellY]["food"].copy():
                        distance = (food.pos - self.pos).Magnitude()
                        if distance <= self.reach:
                            self.simulation.RemoveObject(food)
                            self.food += 1
                            if self.food == 2:
                                break
                    if self.food == 2:
                        break
                if self.food == 2:
                    break

            return True
        self.canStep = False
        return False

    def EvaluateDay(self):
        if self.food == 0:
            return [0]
        elif self.food == 1:
            return [1]
        elif self.food >= 2:
            return [2, self.Reproduce()]

    def Reproduce(self):
        return Creature(self.simulation, self.maxEnergy)


class Food(Base.BaseObject):

    def __init__(self, parentSim, x=0, y=0):
        super().__init__(parentSim)

        self.type = "food"

        self.pos = Base.Vector2(x, y)


graphVisuals = Base.VisualGraphs()
graphVisuals.AddPlot("population", "Population", "Day")

simulation = Base.Simulation(100, 5)

simulation.RegisterNewObject("creature")

startingCreatures = 25

for _ in range(0, startingCreatures):
    simulation.AddNewObject(Creature(simulation, 200))

simulation.RegisterNewObject("food")

simulation.customData.dailyFood = 20000

simulation.data["population"].append(startingCreatures)
graphVisuals.plots["population"][1].setData(simulation.data["population"][:simulation.step])
simulation.step += 1
totalStepTimes = 0


def ThreadedWorker():
    while True:
        task = Q.get()
        if task == "kill":
            Q.task_done()
            break
        task.DoStep()
        Q.task_done()


threads = []
Q = queue.Queue()

if len(threads) == 0:
    for _ in range(0, 10):
        thrd = threading.Thread(target=ThreadedWorker)
        thrd.daemon = True
        thrd.start()
        threads.append(thrd)

stepDrawn = False


def Day():
    global totalStepTimes
    global stepDrawn

    while True:
        if not stepDrawn:
            time.sleep(0.1)
            continue

        timeStart = time.time()

        for _ in range(0, simulation.customData.dailyFood):
            posX = random.randrange(1, simulation.size-1)
            posY = random.randrange(1, simulation.size-1)
            simulation.AddNewObject(Food(simulation, posX, posY))

        for creature in simulation.objects["creature"]:
            creature.StartDay()

        creatureMoved = False
        while True:
            for creature in simulation.objects["creature"]:
                if creature.canStep:
                    Q.put(creature)
                    creatureMoved = True

            if not creatureMoved:
                break
            creatureMoved = False

            Q.join()

        reproducedCreatures = []
        deadCreatures = []
        for creature in simulation.objects["creature"]:
            status = creature.EvaluateDay()
            if status[0] == 0:
                deadCreatures.append(creature)
            elif status[0] == 2:
                reproducedCreatures.append(status[1])

        for creature in reproducedCreatures:
            simulation.AddNewObject(creature)

        for creature in deadCreatures:
            simulation.RemoveObject(creature)

        foodTemp = []
        for food in simulation.objects["food"]:
            foodTemp.append(food)

        print("END OF DAY " + str(simulation.step) + ":")
        print("population: " + str(len(simulation.objects["creature"])))
        print("leftover food: " + str(len(foodTemp)))
        print("time took: " + str(time.time() - timeStart))

        for food in foodTemp:
            simulation.RemoveObject(food)

        simulation.step += 1
        simulation.data["population"].append(len(simulation.objects["creature"]))
        stepDrawn = False


def Update():
    global stepDrawn

    graphVisuals.plots["population"][1].setData(simulation.data["population"][:simulation.step])
    stepDrawn = True


thrd = threading.Thread(target=Day)
thrd.daemon = True
thrd.start()

graphVisuals.SetUpdateFunction(Update, 1000)
graphVisuals.StartProgram()
