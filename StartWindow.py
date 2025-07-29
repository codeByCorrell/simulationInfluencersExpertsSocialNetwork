from PyQt5.QtWidgets import QWidget,QPushButton,QVBoxLayout,QSpinBox,QLabel,QSizePolicy,QGridLayout,QDoubleSpinBox
from Simulation import Simulation
from NetworkWindow import NetworkWindow

class StartWindow(QWidget):
        
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Configurations")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed))
        self.setStyleSheet("background-color: white;")
        self.setMinimumSize(550,250)
        self.createLayout()

    def createLayout(self):
        # start button
        self.startButton = QPushButton("Start",self)
        self.startButton.setStyleSheet("background-color: green; color: white")
        self.startButton.clicked.connect(self.startSim)
        #reset button
        self.resetButton = QPushButton("Reset",self)
        self.resetButton.setStyleSheet("background-color: red; color: white")
        self.resetButton.clicked.connect(self.resetValues)
        # agents section
        self.agentsLabel = QLabel("Agents: ",self)
        self.agentsLabel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        self.agentsSBox = QSpinBox(self)
        self.agentsSBox.setMaximum(100)
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

    def resetValues(self):
        self.agentsSBox.setValue(0)
        self.inflSBox.setValue(0)
        self.expsSBox.setValue(0)
        self.connSBox.setValue(0)
        self.truthSBox.setValue(0.00)
