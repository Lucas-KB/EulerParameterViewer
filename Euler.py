import sys
import numpy as np

from PyQt5.QtCore import Qt, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QSplitter, QFrame, QLabel, QSlider

from pyqtgraph.opengl import GLViewWidget, GLLinePlotItem, GLGridItem

class MathProcessor:
    def getRotationMatrix(self, e):
        return np.array(
            [[e[0] ** 2 + e[1] ** 2 - e[2] ** 2 - e[3] ** 2,
            2 * (e[1] * e[2] + e[0] * e[3]),
            2 * (e[1] * e[3] - e[0] * e[2])],
            [2 * (e[1] * e[2] - e[0] * e[3]),
            e[0] ** 2 - e[1] ** 2 + e[2] ** 2 - e[3] ** 2,
            2 * (e[2] * e[3] + e[0] * e[1])],
            [2 * (e[1] * e[3] + e[0] * e[2]),
            2 * (e[2] * e[3] - e[0] * e[1]),
            e[0] ** 2 - e[1] ** 2 - e[2] ** 2 + e[3] ** 2]]
        )
    
    def getBaseCoordinates(self, e):
        rotationMatrix = self.getRotationMatrix(e)

        # Define canonical base
        a1 = np.array(
            [[1], [0], [0]]
        )
        a2 = np.array(
            [[0], [1], [0]]
        )
        a3 = np.array(
            [[0], [0], [1]]
        )

        # Calculate rotated base
        b1 = np.matmul(rotationMatrix, a1)
        b2 = np.matmul(rotationMatrix, a2)
        b3 = np.matmul(rotationMatrix, a3)

        return b1, b2, b3
    
    def recalculateParameters(self):
        pass

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("Euler parameter visualizer")
        self.resize(700, 500)

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
        self.e0slider.setSliderPosition(1000)
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
        self.e0slider.valueChanged.connect(self.rewriteIndicators)
        self.e1slider.valueChanged.connect(self.rewriteIndicators)
        self.e2slider.valueChanged.connect(self.rewriteIndicators)
        self.e3slider.valueChanged.connect(self.rewriteIndicators)
    
    def draw(self):
        # Create items shown in the plot
        self.canonicalBase = GLLinePlotItem()
        self.rotatedBase = GLLinePlotItem()
        self.grid = GLGridItem()

        self.canonicalBase.setData(
            pos=np.array([
                [0,0,0], [1,0,0],
                [0,0,0], [0,1,0],
                [0,0,0], [0,0,1]
            ]),
            color=(0,0,1,1)
        )

        b1, b2, b3 = self.mathProcessor.getBaseCoordinates(
            [
                self.e0slider.value() / 1000,
                self.e1slider.value() / 1000,
                self.e2slider.value() / 1000,
                self.e3slider.value() / 1000
            ]
        )

        self.rotatedBase.setData(
            pos=np.array([
                [0,0,0], [b1[0], b1[1], b1[2]],
                [0,0,0], [b2[0], b2[1], b2[2]],
                [0,0,0], [b3[0], b3[1], b3[2]]
            ]),
            color=(1,0,0,1)
        )

        # Add items to plot
        self.plotWidget.addItem(self.grid)
        self.plotWidget.addItem(self.canonicalBase)
        self.plotWidget.addItem(self.rotatedBase)

    def redraw(self):
        self.canonicalBase.setData(
            pos=np.array([
                [0,0,0], [1,0,0],
                [0,0,0], [0,1,0],
                [0,0,0], [0,0,1]
            ]),
            color=(0,0,1,1)
        )

        b1, b2, b3 = self.mathProcessor.getBaseCoordinates(
            [
                self.e0slider.value() / 1000,
                self.e1slider.value() / 1000,
                self.e2slider.value() / 1000,
                self.e3slider.value() / 1000
            ]
        )

        self.rotatedBase.setData(
            pos=np.array([
                [0,0,0], [b1[0], b1[1], b1[2]],
                [0,0,0], [b2[0], b2[1], b2[2]],
                [0,0,0], [b3[0], b3[1], b3[2]]
            ]),
            color=(1,0,0,1)
        )

    @pyqtSlot()
    def rewriteIndicators(self):
        self.e0indicator.setText("{:.3f}".format(self.e0slider.value() / 1000))
        self.e1indicator.setText("{:.3f}".format(self.e1slider.value() / 1000))
        self.e2indicator.setText("{:.3f}".format(self.e2slider.value() / 1000))
        self.e3indicator.setText("{:.3f}".format(self.e3slider.value() / 1000))

        self.redraw()





if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()

    win.showMaximized()
    sys.exit(app.exec_())