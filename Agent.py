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
        self.rolemodels = dict()
        self.followers = list()
        self.index = index
        self.ownOpinionMatters = False
        self.weightOwnOpinion = 0
        self.newValue = 0

    def updateOpinion(self):
        self.value = self.newValue
        self.newValue = 0