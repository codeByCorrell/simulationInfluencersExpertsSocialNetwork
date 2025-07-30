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
        self.percOfInflsOverTime = [round(influencers/agents,2)]
        self.percOfExpsOverTime = [round(experts/agents,2)]
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
        self.newConns = np.empty((0,2),dtype=int)

    
    def getAverage(self):
        if len(self.agentsList) == 0:
            return 0
        sumValues = 0
        for agent in self.agentsList:
            sumValues += agent.value
        return round(sumValues/len(self.agentsList),2)
    
    def calculateNewOpinions(self):
        for agent in self.agentsList:
            if agent.role != "expert":
                newValue = agent.weightOwnOpinion * agent.value
                for rolemodel,val in agent.rolemodels.items():
                    newValue += val * rolemodel.value
                agent.newValue = round(newValue,2)

    def nextStep(self):
        self.step += 1
        self.steps.append(self.step)
        self.calculateNewOpinions()
        for agent in self.agentsList:
            if agent.role != "expert":
                agent.updateOpinion()
        self.average = self.getAverage()
        self.averages.append(self.average)
        self.percOfExpsOverTime.append(round(self.experts/self.agents,2))
        self.percOfInflsOverTime.append(round(self.influencers/self.agents,2))
        self.updatedValues.emit()

    def plotResults(self):
        plt.plot(self.steps,self.averages,label="Average Opinion")
        plt.plot(self.steps,[self.truth]*len(self.steps),label="Truth")
        plt.plot(self.steps,self.percOfInflsOverTime,label="Percentage of influencers")
        plt.plot(self.steps,self.percOfExpsOverTime,label="Percentage of experts")
        plt.xlabel("Steps")
        plt.ylabel("Opinion Value / Percentage of influencers or experts")
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
        self.average = self.getAverage()
        self.averages.append(self.average)

    def addSingleAgent(self,role:str) -> Agent:
        x = rd.randint(0,100)
        y = rd.randint(0,100)
        posPair = np.array([[x,y]])
        val = round(rd.uniform(0.00,1.00),2) if role != "expert" else self.truth
        id = len(self.agentsList)
        self.positions = np.vstack([self.positions,posPair])
        newAg = Agent(posPair,role,val,id)
        self.agentsList.append(newAg)
        self.connLim = round(0.2*len(self.agentsList),0)
        self.average = self.getAverage()
        self.averages[-1] = self.average
        if role == "influencer":
            self.influencers += 1
        elif role == "expert":
            self.experts += 1
        else:
            self.agents += 1
        return newAg

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

    def createConnectionsForNewAgent(self,agent:Agent):
        self.newConns = np.empty((0,2),dtype=int)
        newFollowersNbr = rd.randint(0,self.connLim - 1)
        for i in range(newFollowersNbr):
            followerId = rd.randint(0,len(self.agentsList)-1)
            agent.ownOpinionMatters = True if agent.index == followerId else False
            follower = self.agentsList[followerId]
            follower.rolemodels[agent] = 0
            agent.followers.append(follower)
            newConn = np.array([[followerId,agent.index]])
            self.connectionsList = np.vstack([self.connectionsList,newConn])
            self.newConns = np.vstack([self.newConns,newConn])
            self.connections += 1

        newRolemodelsNbr = rd.randint(0,self.connLim - 1)
        for j in range(newRolemodelsNbr):
            rolemodelId = rd.randint(0,len(self.agentsList) - 1)
            agent.ownOpinionMatters = True if agent.index == rolemodelId else False
            rolemodel = self.agentsList[rolemodelId]
            rolemodel.followers.append(agent)
            agent.rolemodels[rolemodel] = 0
            newConn = np.array([[agent.index,rolemodelId]])
            self.connectionsList = np.vstack([self.connectionsList,newConn])
            self.newConns = np.vstack([self.newConns,newConn])
            self.connections += 1


    def createInfluencers(self):
        for agent in self.agentsList:
            if agent.role == "influencer":
                self.makeAgentToInfluencer(agent)
    
    def makeAgentToInfluencer(self,agent:Agent):
        followerCounter = 0
        while followerCounter != self.connLim:
            rdAgentId = rd.randint(0,len(self.agentsList)-1)
            newFollower = self.agentsList[rdAgentId]
            if newFollower not in agent.followers:
                newConn = np.array([[rdAgentId,agent.index]])
                self.connectionsList = np.vstack([self.connectionsList,newConn])
                self.newConns = np.vstack([self.newConns,newConn])
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

    def deleteAgent(self,roleStr:str):
        for agent in self.agentsList:
            deletedAgent = False
            if agent.role == roleStr:
                self.agentsList.remove(agent)
                self.positions = np.delete(self.positions,agent.index,axis=0)
                counter = 0
                for con in self.connectionsList:
                    if agent.index in con:
                        self.connectionsList = np.delete(self.connectionsList,counter,axis=0)
                    else:
                        counter += 1
                for idx1,con in enumerate(self.connectionsList):
                    for idx2,idVal in enumerate(con):
                        if idVal > agent.index:
                            self.connectionsList[idx1][idx2] -= 1
                for ag in self.agentsList:
                    if ag.index > agent.index:
                        ag.index -= 1
                    try:
                        ag.followers.remove(agent)
                    except ValueError:
                        pass
                    try:
                        ag.rolemodels.pop(agent)
                    except KeyError:
                        pass
                deletedAgent = True
                break
        if not deletedAgent:
            print(f"There is no {roleStr} left to delete!") 
        else:
            self.connLim = round(0.2*len(self.agentsList),0)
            self.average = self.getAverage()
            self.averages[-1] = self.average
            if roleStr == "influencer":
                self.influencers -= 1
            elif roleStr == "expert":
                self.experts -= 1
            