import pyqtgraph as pg
from PyQt5 import QtGui, QtCore
import random

data = []

app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.setWindowTitle("Test")
mw.resize(800, 800)

pw = pg.PlotWidget(name="plot1")
mw.setCentralWidget(pw)
mw.show()

step = 0
value = 5

def update():
    global step
    global value

    data.append(value)
    value += random.randrange(-1, 2)

    pw.plot(data[:step])
    step += 1

t = QtCore.QTimer()
t.timeout.connect(update)
t.start(1000)


pg.QtGui.QApplication.exec_()
