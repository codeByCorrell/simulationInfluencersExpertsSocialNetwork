from PyQt5.QtCore import pyqtSignal,QObject,QCoreApplication
import matplotlib.pyplot as plt

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
        self.step = 0
        self.steps = [0]
        self.average = 0
        self.averages = list()

    def getAverage(self):
        if len(self.agentsList) == 0:
            return 0
        sumValues = 0
        for agent in self.agentsList:
            sumValues += agent.value
        return round(sumValues/len(self.agentsList),2)
    
    def calculateNewOpinions(self):
        for agent in self.agentsList:
            newValue = agent.weightOwnOpinion * agent.value
            for rolemodel,val in agent.rolemodels.items():
                newValue += val * rolemodel.value
            agent.newValue = round(newValue,2)

    def nextStep(self):
        self.step += 1
        self.steps.append(self.step)
        self.calculateNewOpinions()
        for agent in self.agentsList:
            agent.updateOpinion()
        self.average = self.getAverage()
        self.averages.append(self.average)
        self.updatedValues.emit()

    def plotResults(self):
        plt.plot(self.steps,self.averages,label="Average Opinion")
        plt.plot(self.steps,[self.truth]*len(self.steps),label="Truth")
        plt.xlabel("Steps")
        plt.ylabel("Opinion Value")
        plt.title("Average Opinion and Truth over Steps")
        plt.show()

    def stopSimulation(self):
        QCoreApplication.quit()