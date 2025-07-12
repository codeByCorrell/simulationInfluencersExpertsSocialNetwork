from PyQt5.QtWidgets import QApplication
import sys
from windows import startWindow

app = QApplication(sys.argv)

window1 = startWindow()
window1.show()

app.exec()
