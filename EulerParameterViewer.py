import sys
import numpy as np

from PyQt5.QtCore import Qt, QObject, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QFrame,
    QLabel,
    QSlider,
)

from pyqtgraph.opengl import GLViewWidget, GLLinePlotItem, GLGridItem


class MathProcessor:
    def __init__(self):
        self.queue = list(range(4))

    def getRotationMatrix(self, e):
        return np.array(
            [
                [
                    e[0] ** 2 + e[1] ** 2 - e[2] ** 2 - e[3] ** 2,
                    2 * (e[1] * e[2] + e[0] * e[3]),
                    2 * (e[1] * e[3] - e[0] * e[2]),
                ],
                [
                    2 * (e[1] * e[2] - e[0] * e[3]),
                    e[0] ** 2 - e[1] ** 2 + e[2] ** 2 - e[3] ** 2,
                    2 * (e[2] * e[3] + e[0] * e[1]),
                ],
                [
                    2 * (e[1] * e[3] + e[0] * e[2]),
                    2 * (e[2] * e[3] - e[0] * e[1]),
                    e[0] ** 2 - e[1] ** 2 - e[2] ** 2 + e[3] ** 2,
                ],
            ]
        )

    def getBaseCoordinates(self, e):
        rotationMatrix = self.getRotationMatrix(e)

        # Define canonical base
        a1 = np.array([[1], [0], [0]])
        a2 = np.array([[0], [1], [0]])
        a3 = np.array([[0], [0], [1]])

        # Calculate rotated base
        b1 = np.matmul(rotationMatrix, a1)
        b2 = np.matmul(rotationMatrix, a2)
        b3 = np.matmul(rotationMatrix, a3)

        return b1, b2, b3

    def recalculateParameters(self, e, changedCode):
        self.queue.remove(changedCode)

        for i in self.queue:
            sumRest = 0
            for j in range(4):
                if i != j:
                    sumRest += e[j] ** 2
            if sumRest <= 1:
                e[i] = np.sqrt(1 - sumRest)
                break

        self.queue.append(changedCode)

        return e


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("Euler parameter visualizer")
        self.resize(700, 500)

        # Create array to store the Euler parameter
        self.eulerParam = np.array([1.0, 0.0, 0.0, 0.0])

        # Create central widget and add Layout
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QGridLayout(self.centralwidget)

        # Set horizontal splitter
        self.splitter = QSplitter(Qt.Horizontal, self.centralwidget)

        # Create 3D plot widget
        self.plotWidget = GLViewWidget(self.splitter)

        # Create side bar
        self.sideBar = QFrame(self.splitter)
        self.sideBar.setFrameShape(QFrame.StyledPanel)
        self.sideBar.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.sideBar)

        # Add controls and labels to the side bar

        # e0
        self.e0frame = QFrame(self.sideBar)
        self.e0layout = QHBoxLayout(self.e0frame)
        self.e0label = QLabel("e0", self.e0frame)
        self.e0slider = QSlider(Qt.Horizontal, self.e0frame)
        self.e0slider.setMaximum(1000)
        self.e0slider.setMinimum(0)
        self.e0slider.setSingleStep(1)
        self.e0slider.setPageStep(5)
        self.e0slider.setSliderPosition(int(1000 * self.eulerParam[0]))
        self.e0indicator = QLabel("1.000", self.e0frame)
        self.e0layout.addWidget(self.e0label)
        self.e0layout.addWidget(self.e0slider)
        self.e0layout.addWidget(self.e0indicator)

        # e1
        self.e1frame = QFrame(self.sideBar)
        self.e1layout = QHBoxLayout(self.e1frame)
        self.e1label = QLabel("e1", self.e1frame)
        self.e1slider = QSlider(Qt.Horizontal, self.e1frame)
        self.e1slider.setMaximum(1000)
        self.e1slider.setMinimum(0)
        self.e1slider.setSingleStep(1)
        self.e1slider.setPageStep(5)
        self.e1slider.setSliderPosition(int(1000 * self.eulerParam[1]))
        self.e1indicator = QLabel("0.000", self.e1frame)
        self.e1layout.addWidget(self.e1label)
        self.e1layout.addWidget(self.e1slider)
        self.e1layout.addWidget(self.e1indicator)

        # e2
        self.e2frame = QFrame(self.sideBar)
        self.e2layout = QHBoxLayout(self.e2frame)
        self.e2label = QLabel("e2", self.e2frame)
        self.e2slider = QSlider(Qt.Horizontal, self.e2frame)
        self.e2slider.setMaximum(1000)
        self.e2slider.setMinimum(0)
        self.e2slider.setSingleStep(1)
        self.e2slider.setPageStep(5)
        self.e2slider.setSliderPosition(int(1000 * self.eulerParam[2]))
        self.e2indicator = QLabel("0.000", self.e2frame)
        self.e2layout.addWidget(self.e2label)
        self.e2layout.addWidget(self.e2slider)
        self.e2layout.addWidget(self.e2indicator)

        # e3
        self.e3frame = QFrame(self.sideBar)
        self.e3layout = QHBoxLayout(self.e3frame)
        self.e3label = QLabel("e3", self.e3frame)
        self.e3slider = QSlider(Qt.Horizontal, self.e3frame)
        self.e3slider.setMaximum(1000)
        self.e3slider.setMinimum(0)
        self.e3slider.setSingleStep(1)
        self.e3slider.setPageStep(5)
        self.e3slider.setSliderPosition(int(1000 * self.eulerParam[3]))
        self.e3indicator = QLabel("0.000", self.e3frame)
        self.e3layout.addWidget(self.e3label)
        self.e3layout.addWidget(self.e3slider)
        self.e3layout.addWidget(self.e3indicator)

        # Add all frames to layout
        self.verticalLayout.addWidget(self.e0frame)
        self.verticalLayout.addWidget(self.e1frame)
        self.verticalLayout.addWidget(self.e2frame)
        self.verticalLayout.addWidget(self.e3frame)

        # Lay out the splitter
        self.gridLayout.addWidget(self.splitter)

        # Instantiate MathProcessor
        self.mathProcessor = MathProcessor()

        # First draw
        self.draw()

        # Connect signals
        self.recalculate = True
        self.e0slider.valueChanged.connect(self.onE0Change)
        self.e1slider.valueChanged.connect(self.onE1Change)
        self.e2slider.valueChanged.connect(self.onE2Change)
        self.e3slider.valueChanged.connect(self.onE3Change)

    def draw(self):
        # Create items shown in the plot
        self.canonicalBase = GLLinePlotItem()
        self.canonicalBaseZ = GLLinePlotItem()
        self.rotatedBase = GLLinePlotItem()
        self.rotatedBaseZ = GLLinePlotItem()
        self.grid = GLGridItem()

        self.redraw()

        # Add items to plot
        self.plotWidget.addItem(self.grid)
        self.plotWidget.addItem(self.canonicalBase)
        self.plotWidget.addItem(self.canonicalBaseZ)
        self.plotWidget.addItem(self.rotatedBase)
        self.plotWidget.addItem(self.rotatedBaseZ)

    def redraw(self):
        self.rewriteIndicators()

        self.canonicalBase.setData(
            pos=np.array([[0, 0, 0], [1, 0, 0], [0, 0, 0], [0, 1, 0]]),
            color=(0, 0, 1, 1),
        )
        self.canonicalBaseZ.setData(
            pos=np.array([[0, 0, 0], [0, 0, 1]]), color=(0, 1, 1, 1)
        )

        b1, b2, b3 = self.mathProcessor.getBaseCoordinates(
            [
                self.eulerParam[0],
                self.eulerParam[1],
                self.eulerParam[2],
                self.eulerParam[3],
            ]
        )

        self.rotatedBase.setData(
            pos=np.array(
                [
                    [0, 0, 0],
                    [float(b1[0]), float(b1[1]), float(b1[2])],
                    [0, 0, 0],
                    [float(b2[0]), float(b2[1]), float(b2[2])],
                ]
            ),
            color=(1, 0, 0, 1),
        )
        self.rotatedBaseZ.setData(
            pos=np.array([[0, 0, 0], [float(b3[0]), float(b3[1]), float(b3[2])]]),
            color=(1, 1, 0, 1),
        )

    @pyqtSlot()
    def onE0Change(self):
        if self.recalculate:
            self.eulerParam[0] = self.e0slider.value() / 1000
            self.eulerParam = self.mathProcessor.recalculateParameters(
                self.eulerParam, 0
            )
            self.recalculate = False

            self.e0slider.setSliderPosition(int(1000 * self.eulerParam[0]))
            self.e1slider.setSliderPosition(int(1000 * self.eulerParam[1]))
            self.e2slider.setSliderPosition(int(1000 * self.eulerParam[2]))
            self.e3slider.setSliderPosition(int(1000 * self.eulerParam[3]))

            self.recalculate = True

        self.redraw()

    @pyqtSlot()
    def onE1Change(self):
        if self.recalculate:
            self.eulerParam[1] = self.e1slider.value() / 1000
            self.eulerParam = self.mathProcessor.recalculateParameters(
                self.eulerParam, 1
            )
            self.recalculate = False

            self.e0slider.setSliderPosition(int(1000 * self.eulerParam[0]))
            self.e1slider.setSliderPosition(int(1000 * self.eulerParam[1]))
            self.e2slider.setSliderPosition(int(1000 * self.eulerParam[2]))
            self.e3slider.setSliderPosition(int(1000 * self.eulerParam[3]))

            self.recalculate = True

        self.redraw()

    @pyqtSlot()
    def onE2Change(self):
        if self.recalculate:
            self.eulerParam[2] = self.e2slider.value() / 1000
            self.eulerParam = self.mathProcessor.recalculateParameters(
                self.eulerParam, 2
            )
            self.recalculate = False

            self.e0slider.setSliderPosition(int(1000 * self.eulerParam[0]))
            self.e1slider.setSliderPosition(int(1000 * self.eulerParam[1]))
            self.e2slider.setSliderPosition(int(1000 * self.eulerParam[2]))
            self.e3slider.setSliderPosition(int(1000 * self.eulerParam[3]))

            self.recalculate = True

        self.redraw()

    @pyqtSlot()
    def onE3Change(self):
        if self.recalculate:
            self.eulerParam[3] = self.e3slider.value() / 1000
            self.eulerParam = self.mathProcessor.recalculateParameters(
                self.eulerParam, 3
            )
            self.recalculate = False

            self.e0slider.setSliderPosition(int(1000 * self.eulerParam[0]))
            self.e1slider.setSliderPosition(int(1000 * self.eulerParam[1]))
            self.e2slider.setSliderPosition(int(1000 * self.eulerParam[2]))
            self.e3slider.setSliderPosition(int(1000 * self.eulerParam[3]))

            self.recalculate = True

        self.redraw()

    def rewriteIndicators(self):
        self.e0indicator.setText("{:.3f}".format(self.eulerParam[0]))
        self.e1indicator.setText("{:.3f}".format(self.eulerParam[1]))
        self.e2indicator.setText("{:.3f}".format(self.eulerParam[2]))
        self.e3indicator.setText("{:.3f}".format(self.eulerParam[3]))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()

    win.showMaximized()
    sys.exit(app.exec_())
