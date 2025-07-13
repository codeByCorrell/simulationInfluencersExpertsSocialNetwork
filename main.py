from PyQt5.QtWidgets import QApplication
import sys
from windows import StartWindow,NetworkWindow

app = QApplication(sys.argv)

window1 = StartWindow()
window1.show()

app.exec()
