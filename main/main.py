import sys
from PyQt5.QtWidgets import  QApplication
from PyQt5.QtCore import Qt

from UI import MainWeight

if __name__ == "__main__":
        # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    # fix issue #50
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    window = MainWeight()
    window.show()
    app.exec()
     
