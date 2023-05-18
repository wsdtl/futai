import os
from pathlib import Path    
    
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic 

from database.database import DataBaseData



class MyThread(QThread):
    
    def __init__(self, singal, key_dict):
        
        super().__init__()
        self.MyWindow_window_signal = singal
        self.key_dict = key_dict
        
    def run(self):
        sql = DataBaseData()
        type_data, result = sql.select_data(
            len_min=self.key_dict.get("len_min"),
            len_max=self.key_dict.get("len_max"),
            wid_min=self.key_dict.get("wid_min"),
            wid_max=self.key_dict.get("wid_max"),
            shape_data=self.key_dict.get("shape_data"),
            thinck_data=self.key_dict.get("thinck_data")
        )
        
        if type_data == False:
            self.MyWindow_window_signal.emit(str(result))
        else:
            txt = "搜索到以下符合条件的结果：<br>"
            type_data = type_data[1:]
            for val in result:
                txt += f"长度：{val[1]}mm 宽度：{val[2]}mm 形状：{val[3]} 厚度：{val[4]}mm 位于{val[6]}<br>"
            self.MyWindow_window_signal.emit(txt)
        return


class MyWindow(QWidget):
    
    PATH = Path() / os.path.dirname(os.path.abspath(__file__))
    
    # 声明一个信号 只能放在函数的外面
    window_signal = pyqtSignal(str)
    sql_signal = pyqtSignal(str)
    
    
    def  __init__(self):
        
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        
        self.ui = uic.loadUi(self.PATH / "win.ui")
        self.ui.setWindowTitle("自助废料查询系统")
        self.ui.setWindowIcon(QIcon(str(self.PATH / "icon.png"))) # TODO
        
        # 提取需要操作的控件
        self.len_data_min = self.ui.len_data_min    # 长度约束下限
        self.len_data_max = self.ui.len_data_max    # 长度约束上限
        self.wid_data_mix = self.ui.wid_data_min    # 宽度约束下限
        self.wid_data_max = self.ui.wid_data_max    # 宽度约束上限
        self.shape_data = self.ui.shape_data        # 形状约束
        self.thinck_data = self.ui.thinck_data      # 厚度约束 
        self.search = self.ui.search                # 开始搜索
        self.log =self.ui.log                       # 日志栏
        self.windows = self.ui.window               # 结果显示窗口

        # 绑定槽
        self.search.clicked.connect(self.search_start)
        # 绑定信号
        self.window_signal.connect(self.re_windows)  
        self.sql_signal.connect(self.re_log)
        DataBaseData(signal = self.sql_signal)

        
    def search_start(self):
        
        len_min_ = self.len_data_min.toPlainText() if self.len_data_min.toPlainText() != "" else None
        len_max_ = self.len_data_max.toPlainText() if self.len_data_max.toPlainText() != "" else None
        wid_min_ = self.wid_data_mix.toPlainText() if self.wid_data_mix.toPlainText() != "" else None
        wid_max_ = self.wid_data_max.toPlainText() if self.wid_data_max.toPlainText() != "" else None
        shape_data_ = self.shape_data.toPlainText() if self.shape_data.toPlainText() != "" else None
        thinck_data_ = self.thinck_data.toPlainText() if self.thinck_data.toPlainText() != "" else None
        key_dict = dict(len_min = len_min_, len_max = len_max_, wid_min = wid_min_, 
                        wid_max = wid_max_, shape_data = shape_data_, thinck_data = thinck_data_)
        self.my_thread = MyThread(self.window_signal, key_dict)  # 创建线程
        self.my_thread.start()  # 开始线程
    
    def re_windows(self, txt):
        
        self.windows.setText(txt)
        self.windows.repaint()
        
    def re_log(self, txt):
        
        self.log.setText(txt)
        self.log.repaint()

