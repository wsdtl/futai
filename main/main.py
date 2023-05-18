import sys

from PyQt5.QtWidgets import *

from UI.ui_set import MyWindow



if  __name__ == "__main__":
    app = QApplication(sys.argv)
    
    win = MyWindow()
    win.ui.show()
    
    app.exec()