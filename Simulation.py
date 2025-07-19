from PyQt5.QtCore import pyqtSignal,QObject

class Simulation(QObject):
    updatedValues = pyqtSignal()

    def __init__(self,agents:int,influencers:int,experts:int,connections:int,truth:float):
        super().__init__()
        self.agents = agents
        self.influencers = influencers
        self.experts = experts
        self.connections = connections
        self.truth = truth
        self.connLim = round(0.2*agents,0)
        self.agentsList = list()
        self.connectionsList = list()
        self.steps = 0
        self.average = 0

    def getAverage(self):
        sumValues = 0
        for agent in self.agentsList:
            sumValues += agent.value
        return round(sumValues/len(self.agentsList),2)
    
    def calculateNewOpinions(self):
        # todo: somewhere here is a calculation error !
        for agent in self.agentsList:
            newValue = agent.weightOwnOpinion * agent.value
            for rolemodel,val in agent.rolemodels.items():
                newValue += val * rolemodel.value
            agent.newValue = round(newValue,2)

    def nextStep(self):
        self.steps += 1
        self.calculateNewOpinions()
        for agent in self.agentsList:
            agent.updateOpinion()
        self.average = self.getAverage()
        self.updatedValues.emit()