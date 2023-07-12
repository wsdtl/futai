
import sys
import time
from typing import Tuple, Dict, Any
from PyQt5 import QtCore
from PyQt5.QtCore import QByteArray
from PyQt5 import QtBluetooth
from PyQt5.QtWidgets import *

from PyQt5.Qt import *
import sys

from PyQt5.QtWidgets import QWidget


class Blue(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.findBlue()
        self.name = "BT04-A"
        # self.name = "nova 7 5G"
        # self.uuid = "0000ffe0-0000-1000-8000-00805f9b34fb"
        self.uuid: QtBluetooth.QBluetoothUuid = None
        self.serviceUUID: QtBluetooth.QBluetoothUuid = []
        self.but = QPushButton(self)
        self.but.setText("发送")
        self.resize(50, 50)
        self.move(200,200)
    
        self.but.clicked.connect(self.anxia)
    
    def anxia(self):
        print(self.uuid)
        self.characteristicWrite = self.ServiceObject.characteristic(self.uuid)
        print(self.characteristicWrite)
        # 判断特征是否可用
        print(f'isValid:{self.characteristicWrite.isValid()}')
       
        try:
            for x in range(1,4):
                a = self.ServiceObject.writeCharacteristic
                (
                    self.characteristicWrite, 
                    "A".encode("utf-8"),
                    QtBluetooth.QLowEnergyService.WriteWithoutResponse 
                )
                print("发送成功", "A".encode("utf-8"))
        except Exception as e:
            print("没有连接上", e)

    def findBlue(self):
        self.agent = QtBluetooth.QBluetoothDeviceDiscoveryAgent()
        self.agent.setLowEnergyDiscoveryTimeout(5000)
        self.agent.deviceDiscovered.connect(self.connectBlue)
        self.agent.start()
 

    def connectBlue(self, info: QtBluetooth.QBluetoothDeviceInfo):
    	# 过滤低功耗设备
        if info.name() == self.name:
            print(info)
           
            self.controller = QtBluetooth.QLowEnergyController.createCentral(info)
            self.controller.connected.connect(self.connect_Notify)
            # self.controller.disconnected.connect(self.disconnect_Notify)
            # print(3)
            # try:
            self.controller.connectToDevice()
            # except Exception as e:
            #     print(345)
            self.controller.serviceDiscovered.connect(self.addService)
            self.controller.discoveryFinished.connect(self.disFinished)

            print(self.controller)
    
    def connect_Notify(self, *args, **kwargs):
        print(f'连接通知')
        print(f'args: {args}')
        print(f'kwargs: {kwargs}')
        self.controller.discoverServices()
    
    # def disconnect_Notify(*args, **kwargs):
    #     print(f'断开连接通知')
    #     print(f'args: {args}')
    #     print(f'kwargs: {kwargs}')
    
    
    def addService(self, uuid: QtBluetooth.QBluetoothUuid):
        print('发现服务 Service discovered')
        print(f'uuid: {uuid.toString()}')
        self.serviceUUID.append(uuid)
    
    def disFinished(self):
        print("1")
        # for uuid in self.serviceUUID:
        #     print(uuid)
        #     if uuid.toString() == self.uuid:
        self.uuid = self.serviceUUID[-1]
        print("2")
        self.ServiceObject = self.controller.createServiceObject(self.uuid)
        if self.ServiceObject:
            print("链接成功")
            self.ServiceObject.discoverDetails()

            self.ServiceObject.stateChanged.connect(self.state_Changed)
            self.ServiceObject.characteristicWritten.connect(lambda: print("写入"))
            self.ServiceObject.error.connect(lambda: print("错误"))
   
    def state_Changed(self, s):
        print(f'服务状态变化通知:{s} state:{self.ServiceObject.state()}')
        self.uuid = self.ServiceObject.characteristics()[-1].uuid()

if __name__ == '__main__':


    app = QApplication(sys.argv)
    # 创建控件
    windows = Blue()
    windows.show()
    sys.exit(app.exec())
