import sys
    
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic 

# dxn

class MyWindow(QWidget):
    
    def  __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.ui = uic.loadUi("./main/UI/win.ui")
        self.ui.setWindowTitle("自助废料查询系统")
        self.ui.setWindowIcon(QIcon("./main/UI/icon.png")) # TODO
        
        # 提取需要操作的控件
        self.len_data_min = self.ui.len_data_min    # 长度约束下限
        self.len_data_max = self.ui.len_data_max    # 长度约束上限
        self.wid_data_mix = self.ui.wid_data_min    # 宽度约束下限
        self.wid_data_max = self.ui.wid_data_max    # 宽度约束上限
        self.shape_data = self.ui.shape_data        # 形状约束
        self.thinck_data = self.ui.thinck_data      # 厚度约束 
        self.search = self.ui.search                # 开始搜索
        self.log =self.ui.log                       # 日志栏
        self.windows_msg = self.ui.window           # 结果显示窗口

        print("111" + self.len_data_max.toPlainText() + "111")
        print(self.len_data_max.toPlainText() is "")
        

if  __name__ == "__main__":
    app = QApplication(sys.argv)
    
    win = MyWindow().ui
    win.show()
    
    app.exec()