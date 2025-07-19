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

    def nextStep(self):
        print("emit signal")
        self.updatedValues.emit()