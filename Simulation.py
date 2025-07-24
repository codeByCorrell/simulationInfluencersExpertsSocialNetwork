from PyQt5.QtCore import pyqtSignal,QObject,QCoreApplication
import matplotlib.pyplot as plt
import numpy as np
import random as rd
from Agent import Agent

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
        self.connectionsList = np.empty((0,2),dtype=int)
        self.positions = np.empty((0,2),dtype=int)

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

    def addAgents(self):     
        for i in range(self.agents):
            x = rd.randint(0,100)
            y = rd.randint(0,100)
            posPair = np.array([[x,y]])
            if self.influencers > i:
                roleStr = "influencer"
            elif self.influencers + self.experts > i:
                roleStr = "expert"
            else:
                roleStr = "agent"
            val = round(rd.uniform(0.00,1.00),2) if roleStr != "expert" else self.truth
            self.agentsList.append(Agent(posPair,roleStr,val,i))
            self.positions = np.vstack([self.positions,posPair])

    def connectAgents(self):
        for i in range(self.connections):
            agent1Index = rd.randint(0,len(self.agentsList)-1)
            agent2Index = rd.randint(0,len(self.agentsList)-1)
            agent1 = self.agentsList[agent1Index]
            agent2 = self.agentsList[agent2Index]
            if len(agent2.followers) < self.connLim - 1 and agent1Index != agent2Index:
                agent1.rolemodels[agent2] = 0
                agent2.followers.append(agent1)
                newConn = np.array([[agent1Index,agent2Index]])
            else:
                agent1.ownOpinionMatters = True
                newConn = np.array([[agent1Index,agent1Index]])
            self.connectionsList = np.vstack([self.connectionsList,newConn])

    def createInfluencers(self):
        for agent in self.agentsList:
            if agent.role == "influencer":
                followerCounter = 0
                while followerCounter != self.connLim:
                    rdAgentId = rd.randint(0,len(self.agentsList)-1)
                    newFollower = self.agentsList[rdAgentId]
                    if newFollower not in agent.followers:
                        newConn = np.array([[rdAgentId,agent.index]])
                        self.connectionsList = np.vstack([self.connectionsList,newConn])
                        agent.followers.append(newFollower)
                        newFollower.rolemodels[agent] = 0
                        followerCounter += 1

    def calculateListeningWeights(self):
        for agent in self.agentsList:
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
            agent.weightOwnOpinion = basicVal if agent.ownOpinionMatters else 0
            for key in agent.rolemodels.keys():
                if key.role == "influencer":
                    agent.rolemodels[key] = 2 * basicVal
                else:
                    agent.rolemodels[key] = basicVal
        self.average = self.getAverage()
        self.averages.append(self.average)
