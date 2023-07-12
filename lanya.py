#!/usr/bin/env python
# --*--coding=utf-8--*--
# pip install PyQt5
import sys
import time
from PyQt5 import QtCore
from PyQt5.QtCore import QByteArray
from PyQt5 import QtBluetooth as QtBt



class Application(QtCore.QCoreApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = None
        self.controller = None
        self.timer = None
        self.service = None
        self.serviceUUID = list()
        self.ServiceObject = None
        self.Service = None
        self.characteristicWrite = None
        self.characteristicRead_ = None
        self.notification = None
        self.descriptorReadUUID = list()
        self.descriptorWriteUUID = list()
        self.dev_name = ['C0CEF5E80E38', 'BLE HID KBD MICE']
        self.dev_addr = 'C0:CE:F5:E8:0E:38'
        # 要连接的服务UUID
        self.UUID_S = "{6e400001-b5a3-f393-e0a9-e50e24dc4179}"
        # 写特征UUID
        self.UUID_W = "{6e400002-b5a3-f393-e0a9-e50e24dc4179}"
        # 读特征UUID
        self.UUID_R = "{6e400003-b5a3-f393-e0a9-e50e24dc4179}"
        # 启动扫描程序
        self.scan_for_devices()
        print("扫描完成")
        self.exec()

    def display_status(self):
        print("display")
        print(self.agent.isActive(), self.agent.discoveredDevices())
        self.timer.stop()

    def show_info(self, info: QtBt.QBluetoothDeviceInfo):
    	# 过滤低功耗设备
        if int(info.coreConfigurations()) == QtBt.QBluetoothDeviceInfo.LowEnergyCoreConfiguration:
            print('Device discovered')
            print(f'Name: {info.name()}')
            print(f'Addr: {info.address().toString()}')
            print(f'ServUUID: {info.serviceUuids()}')

    def agent_finished(self):
        print('Agent finished')
        for dev in self.agent.discoveredDevices():
            # 通过蓝牙name连接 或者 通过蓝牙地址连接dev.address()
            if self.dev_name[0] == dev.name() or self.dev_name[1] == dev.name():
                print(f'连接设备: {dev.name()}')
                print(f'coreConfigurations: {int(dev.coreConfigurations())}')
                self.controller = QtBt.QLowEnergyController.createCentral(dev)
                self.controller.connected.connect(self.connect_Notify)
                self.controller.error.connect(self.controller_error)
                self.controller.disconnected.connect(self.disconnect_Notify)
                self.controller.serviceDiscovered.connect(self.addService)
                self.controller.discoveryFinished.connect(self.dis_Finished)
                self.controller.connectToDevice()
                break

    def controller_error(self, e):
        error = ["NoError", "UnknownError", "UnknownRemoteDeviceError", "NetworkError", "InvalidBluetoothAdapterError",
                 "ConnectionError"]
        if e < 6:
            print(error[e])
        else:
            print("UnknownError")

    def connect_Notify(self, *args, **kwargs):
        print(f'连接通知')
        print(f'args: {args}')
        print(f'kwargs: {kwargs}')
        self.serviceUUID = list()
        self.controller.discoverServices()

    def disconnect_Notify(*args, **kwargs):
        print(f'断开连接通知')
        print(f'args: {args}')
        print(f'kwargs: {kwargs}')

    def addService(self, uuid: QtBt.QBluetoothUuid):
        print('发现服务 Service discovered')
        print(f'uuid: {uuid.toString()}')
        self.serviceUUID.append(uuid)

    def dis_Finished(self):
        print(f'服务搜索完成')
        for uuid in self.serviceUUID:
            if uuid.toString() == self.UUID_S:
                self.serviceUUID.clear()
                self.serviceUUID.append(uuid)
                self.ServiceObject = self.controller.createServiceObject(uuid)
                break
        if self.ServiceObject is None:
            print(f'服务连接失败')
        else:
            print(f'服务连接成功')
            self.ServiceObject.stateChanged.connect(self.state_Changed)
            self.ServiceObject.characteristicWritten.connect(self.characteristic_Written)
            self.ServiceObject.error.connect(self.service_Error)
            self.ServiceObject.discoverDetails()

    def characteristic_Written(self, info: QtBt.QLowEnergyCharacteristic, value):
        print(f'特征写入变化通知')
        ch = info.uuid().toString() + " - Characteristic written:" + str(value)
        print(f'{ch}')

    def characteristic_Changed(self, info: QtBt.QLowEnergyCharacteristic, value):
        print(f'特征读取变化通知')
        ch = info.uuid().toString() + " - Characteristic read:" + str(value)
        print(f'{ch}')

    def service_Error(self, error):
        ServiceError = ["NoError", "OperationError", "CharacteristicWriteError", "DescriptorWriteError", "UnknownError",
                        "CharacteristicReadError", "DescriptorReadError"]
        if error < 6:
            print(f'error:{error},{ServiceError[error]}, uuid:{self.ServiceObject.serviceUuid().toString()}')

    def state_Changed(self, s):
        print(f'服务状态变化通知:{s} state:{self.ServiceObject.state()}')

        if s == QtBt.QLowEnergyService.DiscoveringServices:
            print(f"正在搜索服务特征... Discovering services...")
            return
        elif s == QtBt.QLowEnergyService.ServiceDiscovered:
            print(f"搜索服务特征完成. Service discovered.")
            self.descriptorReadUUID = list()
            self.descriptorWriteUUID = list()
            for ch in self.ServiceObject.characteristics():
                print(f'特征:{ch.uuid().toString()}')
                if ch.uuid().toString() == self.UUID_W:
                    # 保存要写的特征UUID
                    self.descriptorWriteUUID.append(ch.uuid())
                    # 创建写特征
                    self.create_write_characteristic(ch.uuid())
                if ch.uuid().toString() == self.UUID_R:
                    # 保存要读的特征UUID
                    self.descriptorReadUUID.append(ch.uuid())
                    # 监听读特征
                    self.create_read_notify(ch.uuid())

    def create_write_characteristic(self, uuid: QtBt.QBluetoothUuid):
        data = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
        if self.ServiceObject:
            self.characteristicWrite = self.ServiceObject.characteristic(uuid)
            # 判断特征是否可用
            print(f'isValid:{self.characteristicWrite.isValid()}')
            if self.characteristicWrite.isValid():
                self.ServiceObject.writeCharacteristic(self.characteristicWrite, bytes(data), QtBt.QLowEnergyService.WriteWithResponse)
                print("创建写特征成功，可进行写数据.")
            else:
                print("err:创建写特征失败，写特征不可用.")

    def create_read_notify(self, uuid: QtBt.QBluetoothUuid):
        if self.ServiceObject:
            self.characteristicRead_ = self.ServiceObject.characteristic(uuid)
            # 判断特征是否可用
            print(f'isValid:{self.characteristicRead_.isValid()}')
            if not self.characteristicRead_.isValid():
                print("err:创建读特征失败，读特征不可用.")
                return

            print("创建读特征成功，正在设置监听...")

            # 获取读特征描述符 descriptors()为list
            self.notification = self.characteristicRead_.descriptors()[0]
            # 判断读特征描述符是否可用
            print(f'read_notify.isValid:{self.notification.isValid()}')
            if not self.notification.isValid():
                print("err:读特征描述符不可用，监听失败.")
                return

            # 绑定监听函数
            self.ServiceObject.characteristicChanged.connect(self.characteristic_Changed)
            # 写0x01,0x00启用监听服务
            self.ServiceObject.writeDescriptor(self.notification, bytes.fromhex('0100'))
            print("设置监听服务成功，正在监听数据...")

    def agent_error(self, e):
        error = ["NoError", "InputOutputError", "PoweredOffError", "InvalidBluetoothAdapterError", "UnknownError"]
        if e < 4:
            print(error[e])
        else:
            print(error[4])

    def scan_for_devices(self):
        self.agent = QtBt.QBluetoothDeviceDiscoveryAgent()
        self.agent.setLowEnergyDiscoveryTimeout(5000)

        self.agent.deviceDiscovered.connect(self.show_info)
        self.agent.error.connect(self.agent_error)
        self.agent.finished.connect(self.agent_finished)

        self.timer = QtCore.QTimer(self.agent)
        self.timer.start(5)
        self.timer.timeout.connect(self.display_status)

        self.agent.start()


if __name__ == '__main__':
    app = Application(sys.argv)
