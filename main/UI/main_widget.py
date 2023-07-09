# coding:utf-8
import sys
from typing import Union

from PyQt5.QtCore import (
    Qt,
    QSize, 
    QPoint,
    QThread,
    pyqtSignal
)
from PyQt5.QtGui import(
    QIcon, 
    QIntValidator,               
    QFont, 
    QKeySequence,
    QPixmap
  
)
from PyQt5.QtWidgets import (
    QMenu,
    QDialog,
    QHBoxLayout, 
    QApplication, 
    QVBoxLayout, 
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QAbstractItemView,
    QTableWidgetItem
)
from qframelesswindow import FramelessWindow, StandardTitleBar

from . import imge
from sql import SqlData

class PushButtoneEmnu(QPushButton):
    def __init__(self) -> None:
        super().__init__()
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setStyleSheet(
        """
        QPushButton#menu 
        {
            background-color: #5e7c8a;
            border-radius: 5px;
            font-family: 宋体;
            font-size: 24px;
            text-align: center;
            padding-left: 20px;
            padding-top: 10px;
            padding-right: 20px;
            padding-bottom: 10px;
        }
        QPushButton#menu:hover 
        {
            border: 1px solid #f0f0f0;
        }
        QPushButton#menu:pressed, QPushButton#menu:checked 
        {
            background-color: #f0f0f0;
            border: 1px solid #d3d3d3;
        }                   
        """)

class PushButtonSeek(QPushButton):
    def __init__(self) -> None:
        super().__init__()
        self.setStyleSheet(
        """
        QPushButton#Seek 
        {
            background-color: #d3d3d3;
            border-radius: 5px;
            padding-left: 20px;
            padding-top: 10px;
            padding-right: 20px;
            padding-bottom: 10px;
            border: 1px solid #aaaaaa;
        }
        QPushButton#Seek:hover 
        {
            color: #0db6f5;
        }
        QPushButton#Seek:pressed, QPushButton#Seek:checked 
        {
            background-color: lightblue;
            border: 1px solid #d3d3d3;
        }                   
        """)
        

class TableWidget(QTableWidget):
    
    tabSqlSignal = pyqtSignal(list, list)
    
    def __init__(self) -> None:
        super().__init__()
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # 删除悬停虚线
        self.verticalHeader().setHidden(True) # 删除序号列
        self.setStyleSheet(
        """
        QTableWidget
            {
               outline: none; 
            }          
        QTableWidget:item:selected
            {
                color: #000000;
                background: qlineargradient(spread: pad,x1: 0,y1: 0,x2: 0,y2: 1, stop: 0 lightblue, stop: 1 #b7e9fc);
            }
        QTableWidget:item:hover
            {
                border: 1px solid #000000;
            }
        """)
        # 允许打开上下文菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # 绑定事件
        self.customContextMenuRequested.connect(self.generateMenu)
        self.tabSqlSignal.connect(self.reTable)  

    def sendSql(self, arg: dict) -> None:
        self.thread = TableWidgetThread(self.tabSqlSignal, arg)  # 创建线程
        self.thread.start()  # 开始线程
        return
    
    def reTable(self, tableHead: list, result: list) -> None:
        self.setRowCount(0)  
        # self.clearContents()  # 清空所有行, 不包括表头
        self.clear()
        self.setColumnCount(len(tableHead))
        self.setHorizontalHeaderLabels(tableHead)
        self.setColumnWidth(0, 60)
        items = result
        
        for i in range(len(items)):
            item = items[i]
            row = self.rowCount()
            self.insertRow(row)
            for j in range(len(item)):
                item = QTableWidgetItem(str(items[i][j])) 
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) # 居中显示
                self.setItem(row, j, item)
        self.viewport().update()
        return

    def generateMenu(self, pos: QPoint):
        try:
            content = self.currentItem().text()
        except Exception as e:
            content = None
        # 如果选择的行索引小于2，弹出上下文菜单
        if content:
            menu = QMenu()
            itemCopy = menu.addAction("复制")
            itemLookImg = menu.addAction("查看图片")
            # 转换坐标系
            screenPos = self.mapToGlobal(pos)
            # 被阻塞
            action = menu.exec(screenPos)
            if action == itemCopy:
                clipboard = QApplication.clipboard()
                clipboard.setText(content)
            elif action == itemLookImg:
                row = self.currentRow()
                ID = self.item(row, 0).text()
                self.tipWindow = DialogImg(ID)
                self.tipWindow.open()
            else:
                return
        
class TableWidgetThread(QThread):
    
    def __init__(self, singal: pyqtSignal, arg: dict) -> None:
        super().__init__()
        self.tabSqlSignal = singal
        self.arg = arg
        
    def run(self) -> None:
        sql = SqlData()
        tableHead, result = sql.select_data(
            len_min=self.arg.get("longMin", None),
            len_max=self.arg.get("longMax", None),
            wid_min=self.arg.get("widthMin", None),
            wid_max=self.arg.get("widthMax", None),
            shape_data=self.arg.get("shape", None),
            thinck_data=self.arg.get("thinck", None)
        )
        if not tableHead:
            pass
        else:
            self.tabSqlSignal.emit(list(tableHead), list(result))
        return

class ComboxShape(QComboBox):
    
    boxShapeSingal = pyqtSignal(list)
    
    def __init__(self) -> None: 
        super().__init__()
        self.boxShapeSingal.connect(self.reBoxShape)
        self.sendSql()
        self.setStyleSheet(
        """
        QComboBox
        {
            border-radius:3px;
            background-color: #d3d3d3;
            color: #000000;
            border:0px ;
        }
        """)
    
    def sendSql(self) -> None:
        self.thread = ComboxShapeThread(self.boxShapeSingal)  # 创建线程
        self.thread.start()  # 开始线程
        return
    
    def reBoxShape(self, shapeList: list) -> None:
        self.addItems(shapeList)

class ComboxShapeThread(QThread):
    
    def __init__(self, singal: pyqtSignal) -> None:
        super().__init__()
        self.boxShapeSingal = singal
        
    def run(self) -> None:
        sql = SqlData()
        result = sql.select_shape_all()
        if result:
            shapeList = list()
            shapeList.append("所有形状")
            for x in result:
                shapeList.append(str(x[0]))
            self.boxShapeSingal.emit(shapeList)
        return

class LineEdit(QLineEdit):
    def __init__(self) ->None:
        super().__init__()
        self.setStyleSheet(
        """
        QLineEdit
        {
            border: 1px solid #aaaaaa;
            border-radius:3px;
            background-color: #ffffff;
            color: #000000;
        }
        """)
  
class DialogImg(QDialog):
    
    dialogSingal = pyqtSignal(str)
    
    def __init__(self, ID: Union[int, str]):
        super().__init__()
        self.setWindowTitle(f"序号{ID}物料的图片预览")
        self.setWindowIcon(QIcon(":img/icon.png"))
        self.lab = QLabel(self)
        self.thread = DialogImgThread(self.dialogSingal, ID)  # 创建线程
        self.thread.start()  # 开始线程
        self.dialogSingal.connect(self.reDialog)  
    
    def reDialog(self, path: str):
        self.image = QPixmap(path)
        self.resize(self.image.width(), self.image.height())
        self.lab.setGeometry(0, 0, self.image.width(), self.image.height())
        self.lab.setPixmap(self.image)

class DialogImgThread(QThread):

    def __init__(self, singal: pyqtSignal, ID: Union[int, str]) -> None:
        super().__init__()
        self.dialogSingal = singal
        self.ID = ID
        
    def run(self) -> None:
        sql = SqlData()
        imgUrl = sql.select_img_url(self.ID)
        if imgUrl:
            self.dialogSingal.emit(str(imgUrl))
        else:
            self.dialogSingal.emit(":img/noimage.png")
        return
    
    
class mainWeight(FramelessWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(1000, 800)
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.setDoubleClickEnabled(False)
        self.titleBar.maxBtn.deleteLater()  # 删除最大化按钮
        self.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.setResizeEnabled(False)  # 禁止手动拉伸
        self.setWindowTitle("FuTai")
        self.setWindowIcon(QIcon(":img/icon.png"))  # 图标
        self.setObjectName("FramelessWindow")
        self.setStyleSheet("""
            QWidget#FramelessWindow
            { 
                background: #ffffff;
            }
        """)
        self.mainWidget = QWidget(self)
        self.mainWidget.setObjectName("mainWidget")
        self.mainWidget.resize(self.width(), self.height() - 35)
        self.mainWidget.move(0, 35)
        self.mainWidget.setStyleSheet(
            """QWidget#mainWidget
            {
                background: #f0f0f0;
                border: 1px solid #dcdfe6;
            }                   
        """)
        self.setAllLayout()
        self.initLeft()
        self.initRight()
        
    def setAllLayout(self) -> None:

        self.mainLayout = QHBoxLayout(self.mainWidget)
        
        self.leftWidget = QWidget()
        self.leftWidget.setObjectName("leftWidget")
        self.leftWidget.setStyleSheet(
            """QWidget#leftWidget
            {
                background: #5e7c8a;
                border: 1px solid #dcdfe6;
            }
        """)
        self.leftLayout = QVBoxLayout(self.leftWidget)
        
        self.rightWidget = QWidget()
        self.rightWidget.setObjectName("rightWidget")
        self.rightWidget.setStyleSheet(
            """QWidget#rightWidget
            {
                background: #ffffff;
                border: 1px solid #dcdfe6;
            }
        """)
        self.rightLayout = QVBoxLayout(self.rightWidget)
        
        self.mainLayout.addWidget(self.leftWidget, 1)
        self.mainLayout.addWidget(self.rightWidget, 7)
         
        self.rightWidgetBase = None

    def initLeft(self) -> None:
        self.menuQuery = PushButtoneEmnu()
        self.menuQuery.setObjectName("menu")
        self.menuQuery.setText("物料查询")
        self.leftLayout.addWidget(self.menuQuery)
        
        self.menuRoot = PushButtoneEmnu()
        self.menuRoot.setObjectName("menu")
        self.menuRoot.setText("小车定位")
        self.leftLayout.addWidget(self.menuRoot)
        
        self.menuGet = PushButtoneEmnu()
        self.menuGet.setObjectName("menu")
        self.menuGet.setText("数据获取")
        self.leftLayout.addWidget(self.menuGet)
        
        self.menuWrite = PushButtoneEmnu()
        self.menuWrite.setObjectName("menu")
        self.menuWrite.setText("数据录入")
        self.leftLayout.addWidget(self.menuWrite)
        
        self.menuSet = PushButtoneEmnu()
        self.menuSet.setObjectName("menu")
        self.menuSet.setText("系统设置")
        self.leftLayout.addWidget(self.menuSet)
        
        self.menuHelp = PushButtoneEmnu()
        self.menuHelp.setObjectName("menu")
        self.menuHelp.setText("获取帮助")
        self.leftLayout.addWidget(self.menuHelp)
        self.leftLayout.addStretch(1)

        self.menuQuery.clicked.connect(self.drawQuery)
        self.menuRoot.clicked.connect(self.drawRoot)
        self.menuGet.clicked.connect(self.drawGet)
        self.menuWrite.clicked.connect(self.drawWrite)
        self.menuSet.clicked.connect(self.drawSet)
        self.menuHelp.clicked.connect(self.drawHelp)
    
    def initRight(self) -> None:
        if not self.rightLayout:
            self.drawQuery()
            self.rightLayout.addWidget(self.rightWidgetBase)
            self.menuQuery.setChecked(True)
            
    def drawQuery(self) -> None:
        if self.rightLayout:
            self.rightLayout.removeWidget(self.rightWidgetBase)
        self.rightWidgetBase = QWidget()
        self.rightWidgetBase.setStyleSheet("font-family: Microsoft YaHei;font-size: 16px;")
        
        vQueryLayout = QVBoxLayout(self.rightWidgetBase)
        
        hQueryOne = QHBoxLayout()
        labLong = QLabel()
        labLong.setText("长度区间")
        self.editLongMin = LineEdit()
        self.editLongMin.setPlaceholderText("下限 mm")
        self.editLongMin.setValidator(QIntValidator()) # 只能输入整型
        self.editLongMax = LineEdit()
        self.editLongMax.setPlaceholderText("上限 mm")
        self.editLongMax.setValidator(QIntValidator())
        hQueryOne.addWidget(labLong)
        hQueryOne.addWidget(self.editLongMin, 2)
        hQueryOne.addWidget(self.editLongMax, 2)
        
        labWidth = QLabel()
        labWidth.setText("宽度区间")
        self.editWidthMin = LineEdit()
        self.editWidthMin.setPlaceholderText("下限 mm")
        self.editWidthMin.setValidator(QIntValidator()) # 只能输入整型
        self.editWidthMax = LineEdit()
        self.editWidthMax.setPlaceholderText("上限 mm")
        self.editWidthMax.setValidator(QIntValidator()) # 只能输入整型
        hQueryOne.addWidget(labWidth)
        hQueryOne.addWidget(self.editWidthMin, 2)
        hQueryOne.addWidget(self.editWidthMax, 2)
        
        labThinck = QLabel()
        labThinck.setText("厚度")
        self.editThinck = LineEdit()
        self.editThinck.setPlaceholderText("mm")
        self.editThinck.setValidator(QIntValidator()) # 只能输入整型
        hQueryOne.addWidget(labThinck)
        hQueryOne.addWidget(self.editThinck, 2)
        
        labShape = QLabel()
        labShape.setText("形状")
        self.conBoxShape = ComboxShape()
        hQueryOne.addWidget(labShape)
        hQueryOne.addWidget(self.conBoxShape, 3)
        
        hQueryTwo = QHBoxLayout()
        
        self.butSeek = PushButtonSeek()
        self.butSeek.setObjectName("Seek")
        self.butSeek.setText("查找")
        
        hQueryTwo.addStretch(1)
        hQueryTwo.addWidget(self.butSeek)
        self.tabQuery = TableWidget()
        
        vQueryLayout.addLayout(hQueryOne)
        vQueryLayout.addSpacing(5) 
        vQueryLayout.addLayout(hQueryTwo)
        vQueryLayout.addWidget(self.tabQuery)
    
        self.rightLayout.addWidget(self.rightWidgetBase)
        self.butSeek.clicked.connect(self.updataTable)
        
    def updataTable(self) -> None:
        arg = dict()
        if self.editLongMin.text():
            arg["longMin"] = self.editLongMin.text()
        if self.editLongMax.text():
            arg["longMax"] = self.editLongMax.text()
        if self.editWidthMin.text():
            arg["widthMin"] = self.editWidthMin.text()
        if self.editWidthMax.text():
            arg["widthMax"] = self.editWidthMax.text()
        if self.editThinck.text():
            arg["thinck"] = self.editThinck.text()
        if self.conBoxShape.currentText() != "所有形状":
             arg["shape"] = self.conBoxShape.currentText()
        self.tabQuery.sendSql(arg)
        
    def drawRoot(self) -> None:
        if self.rightLayout:
            self.rightLayout.removeWidget(self.rightWidgetBase)
        q1 = QLabel()
        q1.setText("小车定位页面还没有写")
        q1.setStyleSheet("QLabel{font-family: Microsoft YaHei; font-size: 14px; color: #BDC8E2; background-color: #2E3648;}")
        self.rightWidgetBase = q1
        self.rightLayout.addWidget(self.rightWidgetBase)
    
    def drawGet(self) -> None:
        if self.rightLayout:
            self.rightLayout.removeWidget(self.rightWidgetBase)
        q2 = QLabel()
        q2.setText("数据获取页面还没有写")
        q2.setStyleSheet("QLabel{font-family: Microsoft YaHei; font-size: 14px; color: #BDC8E2; background-color: #2E3648;}")
        self.rightWidgetBase = q2
        self.rightLayout.addWidget(self.rightWidgetBase)
    
    def drawWrite(self) -> None:
        if self.rightLayout:
            self.rightLayout.removeWidget(self.rightWidgetBase)
        q3 = QLabel()
        q3.setText("数据录入页面还没有写")
        q3.setStyleSheet("QLabel{font-family: Microsoft YaHei; font-size: 14px; color: #BDC8E2; background-color: #2E3648;}")
        self.rightWidgetBase = q3
        self.rightLayout.addWidget(self.rightWidgetBase)
            
    def drawSet(self) -> None:
        if self.rightLayout:
            self.rightLayout.removeWidget(self.rightWidgetBase)
        q4 = QLabel()
        q4.setText("系统设置页面还没有写")
        q4.setStyleSheet("QLabel{font-family: Microsoft YaHei; font-size: 14px; color: #BDC8E2; background-color: #2E3648;}")
        self.rightWidgetBase = q4
        self.rightLayout.addWidget(self.rightWidgetBase)
            
    def drawHelp(self) -> None:
        if self.rightLayout:
            self.rightLayout.removeWidget(self.rightWidgetBase)
        q5 = QLabel()
        q5.setText("获取帮助页面还没有写")
        q5.setStyleSheet("QLabel{font-family: Microsoft YaHei; font-size: 14px; color: #BDC8E2; background-color: #2E3648;}")
        self.rightWidgetBase = q5
        self.rightLayout.addWidget(self.rightWidgetBase)
            

    

 
def main():
        # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    # fix issue #50
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    window = mainWeight()
    window.show()
    app.exec()
    
    
if __name__ == '__main__':
    main()

    
 