from PyQt5.QtWidgets import QWidget,QPushButton,QVBoxLayout,QHBoxLayout,QLabel,QGridLayout
import pyqtgraph as pg
import numpy as np
import random as rd
from Agent import Agent
from Simulation import Simulation

class NetworkWindow(QWidget):

    def __init__(self,simulation:Simulation):
        super().__init__()
        self.setWindowTitle("Network Simulation")
        self.showMaximized()
        self.setStyleSheet("background-color: black")
        self.sim = simulation
        self.sim.updatedValues.connect(self.updateWindow)
        self.viewTextItems = list()
        self.viewArrowsEdgesItems = list()
        self.createLayout()
        

    def createLayout(self):

        # create an empty view and graph item
        win = pg.GraphicsLayoutWidget(show=True)
        self.view = win.addViewBox()
        self.view.setAspectLocked()
        self.graph = pg.GraphItem()

        # add agents, connect them randomly and create influencers
        self.sim.addAgents()
        self.sim.connectAgents()
        self.sim.createInfluencers()

        # draw the actual graph
        self.updateGraph(self.graph)

        # draw the agents opinions, how much they weigh other opinions and who they are listening to
        self.drawAgentOpinions()
        self.sim.calculateListeningWeights()
        self.drawArrowsAndWeights()

        # Add Buttons
        self.nextStepButton = QPushButton("Next Step",self)
        self.nextStepButton.setStyleSheet("background-color: blue; color: white")
        self.nextStepButton.clicked.connect(self.sim.nextStep)
        self.addInfButton = QPushButton("Add Influencer",self)
        self.addInfButton.setStyleSheet("background-color: green; color: white")
        self.addInfButton.clicked.connect(lambda: self.addAgentToView("influencer"))
        self.addExpButton = QPushButton("Add Expert",self)
        self.addExpButton.setStyleSheet("background-color: green; color: white")
        self.addExpButton.clicked.connect(lambda: self.addAgentToView("expert"))
        self.delInfButton = QPushButton("Delete Influencer",self)
        self.delInfButton.clicked.connect(lambda: self.deleteAgentFromView("influencer"))
        self.delInfButton.setStyleSheet("background-color: red; color: white")
        self.delExpButton = QPushButton("Delete Expert",self)
        self.delExpButton.setStyleSheet("background-color: red; color: white")
        self.delExpButton.clicked.connect(lambda: self.deleteAgentFromView("expert"))
        self.plotButton = QPushButton("Plot Results",self)
        self.plotButton.setStyleSheet("background-color: blue; color: white")
        self.plotButton.clicked.connect(self.sim.plotResults)
        self.stopButton = QPushButton("Stop Simulation")
        self.stopButton.setStyleSheet("background-color: red; color: white")
        self.stopButton.clicked.connect(self.sim.stopSimulation)
        buttonLay = QGridLayout()
        buttonLay.addWidget(self.nextStepButton,0,0,1,2)
        buttonLay.addWidget(self.addInfButton,1,0)
        buttonLay.addWidget(self.addExpButton,1,1)
        buttonLay.addWidget(self.delInfButton,2,0)
        buttonLay.addWidget(self.delExpButton,2,1)
        buttonLay.addWidget(self.plotButton,3,0,1,2)
        buttonLay.addWidget(self.stopButton,4,0,1,2)
      
        # Add Labels
        self.truthLabel = QLabel("Truth: ",self)
        self.truthLabel.setText(f"Truth: {self.sim.truth}")
        self.truthLabel.setStyleSheet("color: blue")
        self.avgLabel = QLabel(f"Average: {self.sim.average}",self)
        self.avgLabel.setStyleSheet("color: blue")
        self.stepsLabel = QLabel("Steps: 0",self)
        self.stepsLabel.setStyleSheet("color: blue")
        self.labelLay = QHBoxLayout()
        self.labelLay.addWidget(self.truthLabel)
        self.labelLay.addWidget(self.avgLabel)
        self.labelLay.addWidget(self.stepsLabel)

        # Create the layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(win)
        self.layout.addLayout(buttonLay)
        self.layout.addLayout(self.labelLay)
        self.setLayout(self.layout)

    def drawAgentOpinions(self):
        for text in self.viewTextItems:
            self.view.removeItem(text)
        self.viewTextItems = list()
        for agent in self.sim.agentsList:
            text = pg.TextItem(str(agent.value), anchor=(0.5, 0.5), color=agent.color)
            text.setPos(agent.pos[0][0], agent.pos[0][1])
            self.view.addItem(text)
            self.viewTextItems.append(text)

    def updateWindow(self):
        self.stepsLabel.setText(f"Steps: {self.sim.step}")
        self.avgLabel.setText(f"Average: {self.sim.average}")
        self.drawAgentOpinions()

    def drawArrowsAndWeights(self):
        for optic in self.viewArrowsEdgesItems:
            self.view.removeItem(optic)
        self.viewArrowsEdgesItems = list()
        for ag1Id, ag2Id in self.sim.connectionsList:
            p1 = self.sim.positions[ag1Id]
            p2 = self.sim.positions[ag2Id]
            dx, dy = p2 - p1
            # check if self loop
            if dx == 0 and dy == 0:
                brushCol = 'r'
                arrowPos = p1 - np.array([0.5,0])
                textPos = p1 - np.array([0.7,0.2])
            else:
                brushCol = 'b'
                arrowPos = p1 + 0.95 * (p2 - p1)
                textPos = p1 + 0.5 * (p2 - p1)
            angle = 180 - float(np.degrees(np.arctan2(dy, dx)))
            arrow = pg.ArrowItem(pos=arrowPos, angle=angle, headLen=30, brush=brushCol)
            self.view.addItem(arrow)
            self.viewArrowsEdgesItems.append(arrow)
            
            agent1 = self.sim.agentsList[ag1Id]
            agent2 = self.sim.agentsList[ag2Id]
            weightVal = agent1.rolemodels[agent2] if agent1 != agent2 else agent1.weightOwnOpinion
            text = pg.TextItem(str(weightVal), anchor=(0.5, 0.5), color='w')
            text.setPos(textPos[0],textPos[1])
            self.view.addItem(text)
            self.viewArrowsEdgesItems.append(text)


    def updateGraph(self,graph:pg.GraphItem):
        graph.setData(
            pos=self.sim.positions,
            adj=self.sim.connectionsList,
            size=40,
            symbol='o',
            pxMode=True,
            symbolBrush='w'
        )
        self.view.addItem(graph)

    def addAgentToView(self,agentRole:str = "agent"):
        newAgent = self.sim.addSingleAgent(agentRole)
        self.sim.createConnectionsForNewAgent(newAgent)
        if agentRole == "influencer":
            self.sim.createInfluencers()
        self.sim.calculateListeningWeights()
        self.updateGraph(self.graph)
        self.drawAgentOpinions()
        self.drawArrowsAndWeights()
        self.avgLabel.setText(f"Average: {self.sim.average}")

    def deleteAgentFromView(self,agentRole:str = "agent"):
        self.sim.deleteAgent(agentRole)
        self.sim.calculateListeningWeights()
        self.updateGraph(self.graph)
        self.drawAgentOpinions()
        self.drawArrowsAndWeights()
        self.avgLabel.setText(f"Average: {self.sim.average}")
        