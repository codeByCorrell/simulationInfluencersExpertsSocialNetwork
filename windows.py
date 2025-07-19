from PyQt5.QtWidgets import QWidget,QPushButton,QVBoxLayout,QHBoxLayout,QSpinBox,QLabel,QSizePolicy,QGridLayout,QDoubleSpinBox
import pyqtgraph as pg
import numpy as np
import random as rd

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
        
        # connect agents randomly
        adj = np.empty((0,2),dtype=int)
        for i in range(self.sim.connections):
            agent1Index = rd.randint(0,len(agents)-1)
            agent2Index = rd.randint(0,len(agents)-1)
            if len(agents[agent2Index].followers) < self.sim.connLim - 1 and agent1Index != agent2Index:
                agents[agent1Index].rolemodels.append(agents[agent2Index])
                agents[agent1Index].rolemodelIds[agent2Index] = 0
                agents[agent2Index].followers.append(agents[agent1Index])
                agents[agent2Index].followerIds.append(agent1Index)
                newConn = np.array([[agent1Index,agent2Index]])
            else:
                agents[agent1Index].ownOpinionMatters = True
                newConn = np.array([[agent1Index,agent1Index]])
            adj = np.vstack([adj,newConn])

        # creating influencers
        for agent in agents:
            if agent.role == "influencer":
                followerCounter = 0
                while followerCounter != self.sim.connLim:
                    rdAgentId = rd.randint(0,len(agents)-1)
                    if rdAgentId not in agent.followerIds:
                        newConn = np.array([[rdAgentId,agent.index]])
                        adj = np.vstack([adj,newConn])
                        follower = agents[rdAgentId]
                        agent.followers.append(follower)
                        agent.followerIds.append(rdAgentId)
                        follower.rolemodels.append(agent)
                        follower.rolemodelIds[agent.index] = 0
                        followerCounter += 1


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
        for agent in agents:
            text = pg.TextItem(str(agent.value), anchor=(0.5, 0.5), color=agent.color)
            text.setPos(agent.pos[0][0], agent.pos[0][1])
            view.addItem(text)
            listensTo = len(agent.rolemodelIds) if not agent.ownOpinionMatters else len(agent.rolemodelIds) + 1
            weightVal = 1 if listensTo == 0 else round(1 / listensTo,2)
            agent.weightOwnOpinion = weightVal
            for key,val in agent.rolemodelIds.items():
                agent.rolemodelIds[key] = weightVal

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
            view.addItem(arrow)
            
            weightVal = agents[ag1Id].rolemodelIds[ag2Id] if ag1Id != ag2Id else agents[ag1Id].weightOwnOpinion
            text = pg.TextItem(str(weightVal), anchor=(0.5, 0.5), color='w')
            text.setPos(textPos[0],textPos[1])
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
        self.connLim = round(0.2*agents,0)

class Agent():

    def __init__(self,position,role,startValue,index):
        self.pos = position
        self.role = role
        self.value = startValue
        if role == "influencer":
            self.color = 'r'
        elif role == "expert":
            self.color = 'g'
        else:
            self.color = 'b'
        self.rolemodels = list()
        self.rolemodelIds = dict()
        self.followers = list()
        self.followerIds = list()
        self.index = index
        self.ownOpinionMatters = False
        self.weightOwnOpinion = 0
