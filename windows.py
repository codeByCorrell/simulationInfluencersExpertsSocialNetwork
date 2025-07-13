from PyQt5.QtWidgets import QWidget,QPushButton,QVBoxLayout,QHBoxLayout,QSpinBox,QLabel,QSizePolicy,QGridLayout
import pyqtgraph as pg
import numpy as np

class StartWindow(QWidget):
        
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Configurations")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed))
        self.setMinimumSize(500,150)
        self.createLayout()

    def createLayout(self):
        # start button
        startButton = QPushButton("Start",self)
        startButton.clicked.connect(self.startSim)
        #reset button
        resetButton = QPushButton("Reset",self)
        # agents section
        agentsLabel = QLabel("Agents: ",self)
        agentsLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        agentsSBox = QSpinBox(self)
        settingsLay = QGridLayout()
        settingsLay.addWidget(agentsLabel,0,0)
        settingsLay.addWidget(agentsSBox,0,1)
        # influencers section
        inflLabel = QLabel("Influencers: ",self)
        inflLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        inflSBox = QSpinBox(self)
        settingsLay.addWidget(inflLabel,1,0)
        settingsLay.addWidget(inflSBox,1,1)
        # experts section
        expsLabel = QLabel("Experts: ",self)
        expsLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        expsSBox = QSpinBox(self)
        settingsLay.addWidget(expsLabel,2,0)
        settingsLay.addWidget(expsSBox,2,1)
        # main layout
        layMain = QVBoxLayout(self)
        layMain.addLayout(settingsLay)
        layMain.addWidget(resetButton)
        layMain.addWidget(startButton)
        self.setLayout(layMain)

    def startSim(self):
        self.window = NetworkWindow()
        self.window.show()
        self.hide()

class NetworkWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Simulation")
        self.createLayout()

    def createLayout(self):

        win = pg.GraphicsLayoutWidget(show=True)
        view = win.addViewBox()
        view.setAspectLocked()

        # Create a GraphItem
        graph = pg.GraphItem()

        # Node positions
        pos = np.array([[0, 0], [1, 0], [0.5, 1]])
        adj = np.array([[0, 1], [1, 2], [2, 0]])

        # Float values for node labels
        node_labels = [0.3, 0.8, 0.65]

        # Provide dummy symbols so nodes are visible
        graph.setData(
            pos=pos,
            adj=adj,
            size=40,
            symbol='o',
            pxMode=True,
            symbolBrush='w'
        )

        view.addItem(graph)

        # Add labels as TextItem
        for i, label in enumerate(node_labels):
            text = pg.TextItem(str(label), anchor=(0.5, 0.5), color='r')
            text.setPos(pos[i][0], pos[i][1])
            view.addItem(text)


        layout = QVBoxLayout()
        layout.addWidget(win)
        self.setLayout(layout)
