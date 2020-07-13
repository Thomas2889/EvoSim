import random

import BaseClasses as Base


class Creature(Base.BaseObject):

    def __init__(self, parentSim, maxEnergy):
        super().__init__(parentSim)

        self.type = "creature"

        self.food = 0
        self.energy = 0

        self.maxEnergy = maxEnergy
        self.lastMoveChoice = 0

    def StartDay(self):
        choice = random.randrange(0, 4)

        choices = [
            {
                "y": self.simulation.sizeY - 1,
                "x": random.randrange(0, self.simulation.sizeX),
                "start": 4
            },
            {
                "y": random.randrange(0, self.simulation.sizeY),
                "x": self.simulation.sizeX - 1,
                "start": 6
            },
            {
                "y": 0,
                "x": random.randrange(0, self.simulation.sizeX),
                "start": 0
            },
            {
                "y": random.randrange(0, self.simulation.sizeY),
                "x": 0,
                "start": 2
            }
        ]

        self.SetPosition(choices[choice]["x"], choices[choice]["y"])
        self.lastMoveChoice = int(choices[choice]["start"])
        self.energy = self.maxEnergy
        self.food = 0

    def DoStep(self):
        if self.energy > 0 and self.food < 2:
            while True:
                choice = random.randrange(0, 12)

                choices = [
                    {
                        "x": 0,
                        "y": 1
                    },
                    {
                        "x": 1,
                        "y": 1
                    },
                    {
                        "x": 1,
                        "y": 0
                    },
                    {
                        "x": 1,
                        "y": -1
                    },
                    {
                        "x": 0,
                        "y": -1
                    },
                    {
                        "x": -1,
                        "y": -1
                    },
                    {
                        "x": -1,
                        "y": 0
                    },
                    {
                        "x": -1,
                        "y": +1
                    },
                ]

                if choice >= 8:
                    choice = self.lastMoveChoice

                choiceVal = choice

                choice = choices[choice]

                if 0 < self.x + choice["x"] < self.simulation.sizeX and 0 < self.y + choice["y"] < self.simulation.sizeY:
                    self.SetPosition(self.x + choice["x"], self.y + choice["y"])
                    self.lastMoveChoice = choiceVal
                    break

            self.energy -= 1

            if len(self.simulation.world[self.x][self.y]["food"]) > 0:
                self.simulation.RemoveObject(self.simulation.world[self.x][self.y]["food"][0])
                self.food += 1

            return True
        return False

    def EvaluateDay(self):
        if self.food == 0:
            return [0]
        elif self.food == 1:
            return [1]
        elif self.food == 2:
            return [2, self.Reproduce()]

    def Reproduce(self):
        return Creature(self.simulation, self.maxEnergy)


class Food(Base.BaseObject):

    def __init__(self, parentSim, x=0, y=0):
        super().__init__(parentSim)

        self.type = "food"

        self.x = x
        self.y = y


graphVisuals = Base.VisualGraphs()
graphVisuals.AddPlot("population", "Population", "Day")

simulation = Base.Simulation(100, 100)

simulation.RegisterNewObject("creature")

startingCreatures = 25

for _ in range(0, startingCreatures):
    simulation.AddNewObject(Creature(simulation, 500))

simulation.RegisterNewObject("food")

simulation.customData.dailyFood = 50

simulation.data["population"].append(startingCreatures)
graphVisuals.plots["population"][1].setData(simulation.data["population"][:simulation.step])
simulation.step += 1


def Day():
    for _ in range(0, simulation.customData.dailyFood):
        while True:
            posX = random.randrange(1, simulation.sizeX)
            posY = random.randrange(1, simulation.sizeY)

            if len(simulation.world[posX][posY]["food"]) == 0:
                simulation.AddNewObject(Food(simulation, posX, posY))
                break

    for creature in simulation.objects["creature"]:
        creature.StartDay()

    creatureMoved = False
    while True:
        for creature in simulation.objects["creature"]:
            moved = creature.DoStep()
            if not creatureMoved:
                creatureMoved = moved
        if not creatureMoved:
            break
        creatureMoved = False

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

    for food in foodTemp:
        simulation.RemoveObject(food)


def Update():
    Day()

    simulation.data["population"].append(len(simulation.objects["creature"]))

    graphVisuals.plots["population"][1].setData(simulation.data["population"][:simulation.step])
    simulation.step += 1


graphVisuals.SetUpdateFunction(Update, 1000)
graphVisuals.StartProgram()
