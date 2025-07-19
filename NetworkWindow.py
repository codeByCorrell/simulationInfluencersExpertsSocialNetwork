from PyQt5.QtWidgets import QWidget,QPushButton,QVBoxLayout,QHBoxLayout,QLabel,QGridLayout
import pyqtgraph as pg
import numpy as np
import random as rd
from Agent import Agent

class NetworkWindow(QWidget):

    def __init__(self,simulation):
        super().__init__()
        self.setWindowTitle("Network Simulation")
        self.showMaximized()
        self.setStyleSheet("background-color: black")
        self.sim = simulation
        self.sim.updatedValues.connect(self.updateWindow)
        self.viewTextItems = list()
        self.createLayout()
        

    def createLayout(self):

        win = pg.GraphicsLayoutWidget(show=True)
        self.view = win.addViewBox()
        self.view.setAspectLocked()

        graph = pg.GraphItem() 
        # distribute agents randomly  
        agents = list()     
        pos = np.empty((0,2),dtype=int)
        for i in range(self.sim.agents):
            x = rd.randint(0,100)
            y = rd.randint(0,100)
            posPair = np.array([[x,y]])
            if self.sim.influencers > i:
                roleStr = "influencer"
            elif self.sim.influencers + self.sim.experts > i:
                roleStr = "expert"
            else:
                roleStr = "agent"
            val = round(rd.uniform(0.00,1.00),2) if roleStr != "expert" else self.sim.truth
            agents.append(Agent(posPair,roleStr,val,i))
            pos = np.vstack([pos,posPair])
        self.sim.agentsList = agents
        
        # connect agents randomly
        adj = np.empty((0,2),dtype=int)
        for i in range(self.sim.connections):
            agent1Index = rd.randint(0,len(agents)-1)
            agent2Index = rd.randint(0,len(agents)-1)
            agent1 = agents[agent1Index]
            agent2 = agents[agent2Index]
            if len(agent2.followers) < self.sim.connLim - 1 and agent1Index != agent2Index:
                agent1.rolemodels[agent2] = 0
                agent2.followers.append(agent1)
                newConn = np.array([[agent1Index,agent2Index]])
            else:
                agent1.ownOpinionMatters = True
                newConn = np.array([[agent1Index,agent1Index]])
            adj = np.vstack([adj,newConn])

        # creating influencers
        for agent in agents:
            if agent.role == "influencer":
                followerCounter = 0
                while followerCounter != self.sim.connLim:
                    rdAgentId = rd.randint(0,len(agents)-1)
                    newFollower = agents[rdAgentId]
                    if newFollower not in agent.followers:
                        newConn = np.array([[rdAgentId,agent.index]])
                        adj = np.vstack([adj,newConn])
                        agent.followers.append(newFollower)
                        newFollower.rolemodels[agent] = 0
                        followerCounter += 1
        self.sim.connectionsList = adj


        # Provide dummy symbols so nodes are visible
        graph.setData(
            pos=pos,
            adj=adj,
            size=40,
            symbol='o',
            pxMode=True,
            symbolBrush='w'
        )
        self.view.addItem(graph)


        # Add labels as TextItem
        for agent in agents:
            self.writeAgentValue()
            summe = 0 if not agent.ownOpinionMatters else 1
            for key in agent.rolemodels.keys():
                if key.role == "influencer":
                    summe += 2
                else:
                    summe += 1
            if summe != 0:
                # influencers per default use only 50% to listen to other agents
                if agent.role == "influencer":
                    listensTo = 0.5
                else:
                    listensTo = 1
                basicVal = round(listensTo/summe,2)
            else:
                basicVal = 1
            agent.weightOwnOpinion = basicVal
            for key in agent.rolemodels.keys():
                if key.role == "influencer":
                    agent.rolemodels[key] = 2 * basicVal
                else:
                    agent.rolemodels[key] = basicVal
        self.sim.average = self.sim.getAverage()

        # add arrows to indicate direction of connection
        for ag1Id, ag2Id in adj:
            p1 = pos[ag1Id]
            p2 = pos[ag2Id]
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
            
            agent1 = agents[ag1Id]
            agent2 = agents[ag2Id]
            weightVal = agent1.rolemodels[agent2] if agent1 != agent2 else agent1.weightOwnOpinion
            text = pg.TextItem(str(weightVal), anchor=(0.5, 0.5), color='w')
            text.setPos(textPos[0],textPos[1])
            self.view.addItem(text)


        # Buttons Section
        self.nextStepButton = QPushButton("Next Step",self)
        self.nextStepButton.setStyleSheet("background-color: blue; color: white")
        self.nextStepButton.clicked.connect(self.sim.nextStep)
        self.addInfButton = QPushButton("Add Influencer",self)
        self.addInfButton.setStyleSheet("background-color: blue; color: white")
        self.addExpButton = QPushButton("Add Expert",self)
        self.addExpButton.setStyleSheet("background-color: blue; color: white")
        self.delInfButton = QPushButton("Delete Influencer",self)
        self.delInfButton.setStyleSheet("background-color: red; color: white")
        self.delExpButton = QPushButton("Delete Expert",self)
        self.delExpButton.setStyleSheet("background-color: red; color: white")
        self.stopButton = QPushButton("Stop Simulation",self)
        self.stopButton.setStyleSheet("background-color: red; color: white")
        buttonLay = QGridLayout()
        buttonLay.addWidget(self.nextStepButton,0,0,1,2)
        buttonLay.addWidget(self.addInfButton,1,0)
        buttonLay.addWidget(self.addExpButton,1,1)
        buttonLay.addWidget(self.delInfButton,2,0)
        buttonLay.addWidget(self.delExpButton,2,1)
        buttonLay.addWidget(self.stopButton,3,0,1,2)
      
        # Labels Section
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

        self.layout = QVBoxLayout()
        self.layout.addWidget(win)
        self.layout.addLayout(buttonLay)
        self.layout.addLayout(self.labelLay)
        self.setLayout(self.layout)

    def writeAgentValue(self):
        for text in self.viewTextItems:
            self.view.removeItem(text)
        self.viewTextItems = list()
        for agent in self.sim.agentsList:
            text = pg.TextItem(str(agent.value), anchor=(0.5, 0.5), color=agent.color)
            text.setPos(agent.pos[0][0], agent.pos[0][1])
            self.view.addItem(text)
            self.viewTextItems.append(text)

    def updateWindow(self):
        self.stepsLabel.setText(f"Steps: {self.sim.steps}")
        self.avgLabel.setText(f"Average: {self.sim.average}")
        self.writeAgentValue()

        