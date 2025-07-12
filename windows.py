from PyQt5.QtWidgets import QWidget,QPushButton,QVBoxLayout,QHBoxLayout,QSpinBox,QLabel,QSizePolicy

class startWindow(QWidget):
    
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Configurations")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed))
        self.createLayout()

    def createLayout(self):
        startButton = QPushButton("Start",self)
        resetButton = QPushButton("Reset",self)
        agentsLabel = QLabel("Agents: ",self)
        agentsLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        agentsSBox = QSpinBox(self)
        inflLabel = QLabel("Influencers: ",self)
        inflLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        inflSBox = QSpinBox(self)
        expsLabel = QLabel("Experts: ",self)
        expsLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        expsSBox = QSpinBox(self)
        agentsLay = QHBoxLayout()
        agentsLay.addWidget(agentsLabel)
        agentsLay.addWidget(agentsSBox)
        inflLay = QHBoxLayout()
        inflLay.addWidget(inflLabel)
        inflLay.addWidget(inflSBox)
        expsLay = QHBoxLayout()
        expsLay.addWidget(expsLabel)
        expsLay.addWidget(expsSBox)
        layMain = QVBoxLayout(self)
        layMain.addLayout(agentsLay)
        layMain.addLayout(inflLay)
        layMain.addLayout(expsLay)
        layMain.addWidget(resetButton)
        layMain.addWidget(startButton)
        self.setLayout(layMain)
        


