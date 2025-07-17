from PyQt5.QtWidgets import QWidget,QPushButton,QVBoxLayout,QHBoxLayout,QSpinBox,QLabel,QSizePolicy,QGridLayout,QDoubleSpinBox
import pyqtgraph as pg
import numpy as np
import random as rd
from PyQt5.QtGui import QPainter, QPen, QPainterPath
from PyQt5.QtCore import QPointF
from PyQt5 import QtGui

class StartWindow(QWidget):
        
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Configurations")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed))
        self.setMinimumSize(550,250)
        self.createLayout()

    def createLayout(self):
        # start button
        self.startButton = QPushButton("Start",self)
        self.startButton.clicked.connect(self.startSim)
        #reset button
        self.resetButton = QPushButton("Reset",self)
        # agents section
        self.agentsLabel = QLabel("Agents: ",self)
        self.agentsLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        self.agentsSBox = QSpinBox(self)
        self.agentsSBox.setMaximum(1000)
        self.settingsLay = QGridLayout()
        self.settingsLay.addWidget(self.agentsLabel,0,0)
        self.settingsLay.addWidget(self.agentsSBox,0,1)
        # influencers section
        self.inflLabel = QLabel("Influencers: ",self)
        self.inflLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        self.inflSBox = QSpinBox(self)
        self.settingsLay.addWidget(self.inflLabel,1,0)
        self.settingsLay.addWidget(self.inflSBox,1,1)
        # experts section
        self.expsLabel = QLabel("Experts: ",self)
        self.expsLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        self.expsSBox = QSpinBox(self)
        self.settingsLay.addWidget(self.expsLabel,2,0)
        self.settingsLay.addWidget(self.expsSBox,2,1)
        # connections section
        self.connLabel = QLabel("Connections: ",self)
        self.connLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        self.connSBox = QSpinBox(self)
        self.connSBox.setMaximum(100000)
        self.settingsLay.addWidget(self.connLabel,3,0)
        self.settingsLay.addWidget(self.connSBox,3,1)
        # truth section
        self.truthLabel = QLabel("Truth: ",self)
        self.truthLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        self.truthSBox = QDoubleSpinBox(self)
        self.truthSBox.setMinimum(0.0)
        self.truthSBox.setMaximum(1.0)
        self.settingsLay.addWidget(self.truthLabel,4,0)
        self.settingsLay.addWidget(self.truthSBox,4,1)
        # main layout
        self.layMain = QVBoxLayout(self)
        self.layMain.addLayout(self.settingsLay)
        self.layMain.addWidget(self.resetButton)
        self.layMain.addWidget(self.startButton)
        self.setLayout(self.layMain)

    def startSim(self):
        agents = self.agentsSBox.value()
        influencers = self.inflSBox.value()
        experts = self.expsSBox.value()
        connections = self.connSBox.value()
        truth = self.truthSBox.value()
        sim = Simulation(agents,influencers,experts,connections,truth)
        self.window = NetworkWindow(sim)
        self.window.show()
        self.hide()

class NetworkWindow(QWidget):

    def __init__(self,simulation):
        super().__init__()
        self.setWindowTitle("Network Simulation")
        self.showMaximized()
        self.sim = simulation
        self.createLayout()

    def createLayout(self):

        win = pg.GraphicsLayoutWidget(show=True)
        view = win.addViewBox()
        view.setAspectLocked()
        # Create a GraphItem
        graph = pg.GraphItem()
        """
        influencer: connected mit mehr als 10 % aller Agenten
        anzahl an connections festlegen

        1) netztwerk mit richitger anzahl an agenten und Verbindungen
        2) Anzahl an influencern und experten anpassen
        """
        pos = np.empty((0,2),dtype=int)
        nodeLabels = list()
        for i in range(self.sim.agents):
            x = rd.randint(0,100)
            y = rd.randint(0,100)
            newAg = np.array([[x,y]])
            pos = np.vstack([pos,newAg])
            nodeLabels.append(round(rd.uniform(0.00,1.00),2))
        adj = np.empty((0,2),dtype=int)
        for i in range(self.sim.connections):
            x = rd.randint(0,self.sim.agents-1)
            y = rd.randint(0,self.sim.agents-1)
            newConn = np.array([[x,y]])
            adj = np.vstack([adj,newConn])
        
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
        for i, label in enumerate(nodeLabels):
            text = pg.TextItem(str(label), anchor=(0.5, 0.5), color='r')
            text.setPos(pos[i][0], pos[i][1])
            view.addItem(text)

        # Buttons Section
        addInfButton = QPushButton("Add Influencer",self)
        addExpButton = QPushButton("Add Expert",self)
        delInfButton = QPushButton("Delete Influencer",self)
        delExpButton = QPushButton("Delete Expert",self)
        buttonLay = QGridLayout()
        buttonLay.addWidget(addInfButton,0,0)
        buttonLay.addWidget(addExpButton,0,1)
        buttonLay.addWidget(delInfButton,1,0)
        buttonLay.addWidget(delExpButton,1,1)

        # Labels Section
        truthLabel = QLabel("Truth: ",self)
        truthLabel.setText(f"Truth: {self.sim.truth}")
        avgLabel = QLabel("Average: ",self)
        stepsLabel = QLabel("Steps: 0",self)
        labelLay = QHBoxLayout()
        labelLay.addWidget(truthLabel)
        labelLay.addWidget(avgLabel)
        labelLay.addWidget(stepsLabel)

        layout = QVBoxLayout()
        layout.addWidget(win)
        layout.addLayout(buttonLay)
        layout.addLayout(labelLay)
        self.setLayout(layout)

class Simulation():

    def __init__(self,agents:int,influencers:int,experts:int,connections:int,truth:float):
        self.agents = agents
        self.influencers = influencers
        self.experts = experts
        self.connections = connections
        self.truth = truth
