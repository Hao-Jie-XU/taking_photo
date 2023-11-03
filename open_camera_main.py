import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
from PyQt5.Qt import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import *
import numpy as np
from open_camera import Ui_MainWindow  # 导入创建的GUI类
import sys
import threading
sys.path.append("../MvImport")
from MvImport.MvCameraControl_class import *
import datetime
import os
from datetime import datetime
from playsound import playsound
import receive_data
import send_data
import photo_updata
import time


global q_value ,q_photo_name,q_photo_str

class mywindow(QtWidgets.QMainWindow, Ui_MainWindow):
    sendAddDeviceName = pyqtSignal()  # 定义一个添加设备列表的信号。
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    g_bExit = False
    camera_information = False  # 获取相机标志
    receive_open = False #标记接收是否打开
    receivedata = ""
    strate_taking = False  #不允许拍照
    opencamera_flay = False  # 打开相机标志
    # ch:创建相机实例 | en:Creat Camera Object
    cam = MvCamera()


    def __init__(self):
        super(mywindow, self).__init__()
        self.parse_config()
        self.setupUi(self)
        # self.connect_and_emit_sendAddDeviceName()
        self.init()
        self.label.setScaledContents(True)  # 图片自适应
        self.label_2.setScaledContents(True)  # 图片自适应
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        #用来判断空格键是否松开
        #self.space_pressed = False

        #定义OK字样为绿色
        self.text_label_6.setStyleSheet("color: green;")
        #定义定时器
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        def hide_label1():
            self.text_label_6.hide()
        self.timer.timeout.connect(hide_label1)

        #定义NG字样为红色
        self.text_label_7.setStyleSheet("color: red;")
        # 定义定时器
        self.timer2 = QTimer()
        self.timer2.setSingleShot(True)
        def hide_label2():
            self.text_label_7.hide()
        self.timer2.timeout.connect(hide_label2)

        # 初始化上一次按下空格键的时间为当前时间
        self.last_time = QDateTime.currentDateTime()
        print("第一次记录时间：", self.last_time)
    def show_label6_and_start_timer(self):
        # 启动定时器，显示字段，5秒后触发隐藏操作
        self.text_label_6.show()
        self.timer.start(5000)

    def show_label7_and_start_timer(self):
    # 启动定时器，显示字段，5秒后触发隐藏操作
        self.text_label_7.show()
        self.timer2.start(5000)

    def init(self):
        # 获取相机信息，并打开相机
        self.pushButton.clicked.connect(self.get_camera_information)
        #self.pushButton.clicked.connect(self.openCamera)
        # 手动，进入相机调试模式，获取视频流
        self.pushButton_2.clicked.connect(self.hand_movement)
        # 拍照
        self.pushButton_3.clicked.connect(self.taking_pictures)
        # 自动，关闭摄像头，继续获取视频流
        self.pushButton_4.clicked.connect(self.automatic)
        # 使用returnPressed信号来绑定回车键事件,输入框回车
        self.text_entry_8.returnPressed.connect(self.check_enter)

    #隐藏OK字样
    def hide_label(self):
        self.text_label_6.hide()

    #判断空格键调用taking_pictures拍照函数
    # def keyPressEvent(self, event):
    #     if self.space_pressed == False:
    #         if event.key() == Qt.Key_Space:
    #             self.taking_pictures()
    #             self.space_pressed = True
    #
    # def keyReleaseEvent(self, event):
    #     self.space_pressed = False

    # 判断空格键调用taking_pictures拍照函数
    def keyPressEvent(self, event):
        # 获取当前按下空格键的时间
        now_time = QDateTime.currentDateTime()
        print("当前时间：",now_time)


        if event.key() == Qt.Key_Space:  # 判断是否按下了空格键
            time_diff = self.last_time.msecsTo(now_time)  # 改为计算毫秒的时间差
            print(time_diff)
            if time_diff >= 1000:  # 时间差大于1000毫秒才执行拍照操作
                self.taking_pictures()  # 执行拍照函数
                self.last_time = now_time  # 更新上一次按下空格键的时间为当前时间
                print("执行后，记录时间：", self.last_time)
            else:
                self.last_time = now_time  # 更新上一次按下空格键的时间为当前时间
                print("未执行，记录时间：", self.last_time)

    #输入框内容判断
    def check_enter(self):
        # LG-GD02-2107010003_ET110升降桌附件包_300
        value = self.text_entry_8.text()
        if bool(value):
            if value.count("_") == 2:
                value1, value2, value3 = value.split("_")
                length = len(value1)
                # 判断value1满足开头是LG,且长度为18
                if value1.startswith("LG") and len(value1) == 18:
                    # 判断value3是否能转换为float类型
                    if isinstance(value3, str):
                        try:
                            # value1赋值给text_entry_1，并显示到界面上，工单号
                            self.text_entry_1.setText(value1)
                            self.label.setText(value1)
                            # value2赋值给text_entry_2，并显示到界面上，品名
                            self.text_entry_2.setText(value2)
                            self.label.setText(value2)
                            # value3赋值给text_entry_3，并显示到界面上，数量
                            self.text_entry_3.setText(value3)
                            self.label.setText(value3)
                            # 清除内容
                            self.text_entry_8.clear()
                        except ValueError:
                            QMessageBox.critical(self, '错误', '结尾不是数量！')
                else:
                    QMessageBox.critical(self, '错误', '输入内容不是工单！')
            else:
                QMessageBox.critical(self, '错误', '输入的格式不符合要求！')
        else:
            return None

    # 获得所有相机的列表存入cmbSelectDevice中
    def get_camera_information(self):
        self.receive_open = 'False'
        '''选择所有能用的相机到列表中，
             gige相机需要配合 sdk 得到。
        '''
        # 得到相机列表
        # tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
        # ch:枚举设备 | en:Enum device
        ret = MvCamera.MV_CC_EnumDevices(self.tlayerType, self.deviceList)
        if ret != 0:
            print("enum devices fail! ret[0x%x]" % ret)
        if self.deviceList.nDeviceNum == 0:
            QMessageBox.critical(self, "错误", "没有发现设备 ！ ")
        else:
            QMessageBox.information(self, "提示", "发现了 %d 个设备 !" % self.deviceList.nDeviceNum)
        if self.deviceList.nDeviceNum == 0:
            return None
        for i in range(0, self.deviceList.nDeviceNum):
            mvcc_dev_info = cast(self.deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                print("\ngige device: [%d]" % i)
                strModeName = ""
                for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                    strModeName = strModeName + chr(per)
                print("device model name: %s" % strModeName)
        self.camera_information = True
        self.openCamera(self)
        if self.receive_open == 'False':
            thread1 = threading.Thread(target=self.open_port)
            thread1.start()


    #打开端口，接收数据
    def open_port(self):
        current_time = datetime.now()
        # 打印当前时间
        print(f"当前时间：{current_time}")
        receive_data.tcp_interact("127.0.0.1",12345)
        self.receive_open = True

    # 打开摄像头。
    def openCamera(self, camid=0):
        if self.camera_information == True:
            self.g_bExit = False
            self.opencamera_flay = True
            self.strate_taking = True #定义，允许开启自动模式
            # ch:选择设备并创建句柄 | en:Select device and create handle
            stDeviceList = cast(self.deviceList.pDeviceInfo[int(0)], POINTER(MV_CC_DEVICE_INFO)).contents
            ret = self.cam.MV_CC_CreateHandle(stDeviceList)
            if ret != 0:
                # print("create handle fail! ret[0x%x]" % ret)
                QMessageBox.critical(self, "错误", "创建句柄失败 ! ret[0x%x]" % ret)
                # sys.exit()
            # ch:打开设备 | en:Open device
            ret = self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
            if ret != 0:
                # print("open device fail! ret[0x%x]" % ret)
                QMessageBox.critical(self, "错误", "打开设备失败 ! ret[0x%x]" % ret)
                # sys.exit()
            # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
            if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
                nPacketSize = self.cam.MV_CC_GetOptimalPacketSize()
                if int(nPacketSize) > 0:
                    ret = self.cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                    if ret != 0:
                        # print("Warning: Set Packet Size fail! ret[0x%x]" % ret)
                        QMessageBox.warning(self, "警告", "报文大小设置失败 ! ret[0x%x]" % ret)
                else:
                    # print("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)
                    QMessageBox.warning(self, "警告", "报文大小获取失败 ! ret[0x%x]" % nPacketSize)
            # ch:设置触发模式为off | en:Set trigger mode as off
            ret = self.cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            if ret != 0:
                # print("set trigger mode fail! ret[0x%x]" % ret)
                QMessageBox.critical(self, "错误", "设置触发模式失败 ! ret[0x%x]" % ret)
                # sys.exit()
                # ch:获取数据包大小 | en:Get payload size
            stParam = MVCC_INTVALUE()
            memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))

            ret = self.cam.MV_CC_GetIntValue("PayloadSize", stParam)
            if ret != 0:
                # print("get payload size fail! ret[0x%x]" % ret)
                QMessageBox.critical(self, "错误", "获取有效负载大小失败 ! ret[0x%x]" % ret)
                # sys.exit()
            nPayloadSize = stParam.nCurValue

            # ch:开始取流 | en:Start grab image
            ret = self.cam.MV_CC_StartGrabbing()
            if ret != 0:
                # print("start grabbing fail! ret[0x%x]" % ret)
                QMessageBox.critical(self, "错误", "开始抓取图像失败 ! ret[0x%x]" % ret)
                # sys.exit()
            data_buf = (c_ubyte * nPayloadSize)()
            try:
                hThreadHandle = threading.Thread(target=self.work_thread, args=(self.cam, data_buf, nPayloadSize))
                hThreadHandle.start()
            except:
                # print("error: unable to start thread")
                QMessageBox.critical(self, "错误", "无法启动线程 ! ")

        else:
            QMessageBox.critical(self, '错误', '获取相机信息失败！')
            return None

    # 手动
    def hand_movement(self):
        if self.opencamera_flay == True:
            self.label_2.hide() #隐藏拍照界面
            self.label.setGeometry(QtCore.QRect(30, 10, 1440, 980)) #展示视频界面，并定义坐标点
            self.label.show()
            self.strate_taking = False #手动模式下，不能进行拍照
        else:
            QMessageBox.critical(self, '错误', '未打开摄像机！')
            return None

    # 自动
    def automatic(self):
        if self.opencamera_flay == True:
            self.label.setGeometry(QtCore.QRect(1490, 774, 364, 216))  # 展示视频界面，并定义坐标点
            self.label.show()
            self.label_2.show()#显示拍照界面
            self.strate_taking = True #允许进行拍照
        else:
            QMessageBox.critical(self, '错误', '未打开摄像机！')
            return None

    #获取照片，定义照片的分辨率和深度
    def work_thread(self, cam=0, pData=0, nDataSize=0):
        stFrameInfo = MV_FRAME_OUT_INFO_EX()
        memset(byref(stFrameInfo), 0, sizeof(stFrameInfo))
        while True:
            ret = cam.MV_CC_GetOneFrameTimeout(pData, nDataSize, stFrameInfo, 1000)
            if ret == 0:
                image = np.asarray(pData)
                #print(image.shape)
                # 根据自己分辨率进行转化 #5472 × 3648
                #1表示单通道，BGR情况下需要使用3
                image = image.reshape((2048, 2448, 1))
                #image = image.reshape((3648, 5472, 1))

                # Bayer格式（raw data）向RGB或BGR颜色空间的转换，没用,红色显示成绿色
                # 相机的像素格式Bayer RG 8/10/10Packed/12/12Packed 　　YUV422Packed，YUV422_YUYV_Packed 　　RGB 8，BGR 8匹配4种情况，逐个尝试
                image = cv2.cvtColor(image, cv2.COLOR_BAYER_RG2BGR)
                #image = cv2.cvtColor(image, cv2.COLOR_BAYER_GB2BGR)
                #image = cv2.cvtColor(image, cv2.COLOR_BAYER_GR2BGR)
                #image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2BGR)

                #获取时间
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # 在图像上添加时间水印
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1.5
                text_color = (255, 255, 255)  # 白色
                text_thickness = 2
                text_size = cv2.getTextSize(current_time, font, font_scale, text_thickness)[0]
                #水印坐标
                text_position = (image.shape[1] - text_size[0] - 10, image.shape[0] - 10)
                cv2.putText(image, current_time, text_position, font, font_scale, text_color, text_thickness,cv2.LINE_AA)

                # 读取图像高宽深度
                image_height, image_width, image_depth = image.shape
                self.image_show = QImage(image.data, image_width, image_height, image_width * image_depth,
                                         QImage.Format_RGB888)
                self.label.setPixmap(QPixmap.fromImage(self.image_show))
            if self.g_bExit == True:
                del pData
                break

    # 拍照
    def taking_pictures(self):
        #判断相机是否已经打开，并切换至自动模式
        if self.opencamera_flay == True and self.strate_taking == True:
            current_time = datetime.now()  # 将时间转换为字符串格式
            File_Name_1 = self.text_entry_1.text() #获取工单号
            File_Name_2 = self.text_entry_2.text() #获取产品型号
            File_Name_3 = self.text_entry_3.text() #获取数量
            File_Name_4 = self.text_entry_4.text() #获取班组
            File_Path = self.text_entry_5.text() #获取文件路径
            if type == '禁用':
                vm_type = type
            else:
                # 设定是否需要使用visionmaster
                vm_type = self.comboBox_1.currentText()
            #print(vm_type)

            host = "127.0.0.1"
            port = 7930
            global q_value, q_photo_name, q_photo_str
            start_time2 = time.perf_counter()
            #判断工单号、产品型号、数量、班组、文件路径是否存在空值
            if  bool(File_Name_1) and bool(File_Name_2) and bool(File_Name_3) and bool(File_Name_4) and bool(File_Path) :
                folder_name = File_Path + "\\" +  File_Name_1 + " " + File_Name_2 + " " + File_Name_3 + " " + File_Name_4
                # 判断文件夹是否存在
                if not os.path.exists(folder_name):
                    # 创建文件夹
                    os.makedirs(folder_name)
                    #获取当前时间
                    time_str = current_time.strftime("%Y-%m-%d %H%M%S")
                    #存储照片，照片名字为当前时间
                    file_path = os.path.join(folder_name, time_str + '.bmp')
                    self.image_show.save(file_path)# 保存图片到指定文件夹下
                    # 显示照片
                    self.label_2.setPixmap(QtGui.QPixmap.fromImage(self.image_show))
                    print(self.receivedata)
                    if vm_type == "启用":
                    #获取软件调用visionmaster的调用结果
                        get_value = send_data.send_data(host, port, file_path)
                    else:
                        get_value = "NG"
                    # 判断软件和visionmaster的通信是否成功
                    if get_value == 'OK' :
                        #获取visionmaster的返回结果
                        receive_value = receive_data.get_data()
                        if receive_value == "OK":
                            #播放拍照OK字样，线程
                            thread2 = threading.Thread(target=self.play_OK_mp3)
                            thread2.start()
                            self.show_label6_and_start_timer()
                        else:
                            self.show_label7_and_start_timer()
                            thread6 = threading.Thread(target=self.play_NG_mp3)
                            thread6.start()
                            #删除上面的照片
                            #os.remove(file_path)
                        q_value = receive_value
                        q_photo_name = folder_name
                        q_photo_str = time_str
                        thread_updata = threading.Thread(target=self.photo)
                        thread_updata.start()
                    else:
                        thread9 = threading.Thread(target=self.play_OK_mp3)
                        thread9.start()
                        self.show_label6_and_start_timer()
                else:
                    time_str = current_time.strftime("%Y-%m-%d %H%M%S")
                    file_name = time_str + '.bmp'
                    file_path = os.path.join(folder_name, file_name)
                    self.image_show.save(file_path)
                    self.label_2.setPixmap(QtGui.QPixmap.fromImage(self.image_show))
                    if vm_type == "启用":
                        # 获取软件调用visionmaster的调用结果
                        get_value = send_data.send_data(host, port, file_path)
                    else:
                        get_value = "NG"
                    if get_value == 'OK' :
                        receive_value = receive_data.get_data()
                        if receive_value == "OK":
                            thread3 = threading.Thread(target=self.play_OK_mp3)
                            thread3.start()
                            self.show_label6_and_start_timer()
                        else:
                            self.show_label7_and_start_timer()
                            thread7 = threading.Thread(target=self.play_NG_mp3)
                            thread7.start()
                            #删除上面的照片
                            # os.remove(file_path)
                        q_value = receive_value
                        q_photo_name = folder_name
                        q_photo_str = time_str
                        thread_updata_2 = threading.Thread(target=self.photo)
                        thread_updata_2.start()
                    else:
                        thread8 = threading.Thread(target=self.play_OK_mp3)
                        thread8.start()
                        self.show_label6_and_start_timer()
            else :
                # 添加线程执行失败音效
                thread4 = threading.Thread(target=self.play_NG_mp3)
                thread4.start()
                #QMessageBox.critical(self, "错误", "有一个或多个值为空")
        else:
            # 添加线程执行失败音效
            thread5 = threading.Thread(target=self.play_NG_mp3)
            thread5.start()
            #QMessageBox.critical(self, '错误', '未进入自动模式！')
            return None
        end_time2 = time.perf_counter()
        duration = end_time2 - start_time2
        #print(f"代码执行时长: {duration:.2f}秒")


    def photo(self):
        get_value = q_value
        get_photo_name = q_photo_name
        get_photo_str = q_photo_str
        photo_updata(get_value, get_photo_name, get_photo_str)

    #拍照成功音效
    def play_OK_mp3(self):
        sound_path_OK = self.text_entry_6.text()
        #判断文件是否存在，不存在则不播放
        if os.path.exists(sound_path_OK):
            #地址格式转换
            decoded_path = sound_path_OK.encode('utf-8').decode('utf-8')
            playsound(decoded_path)

    # 拍照失败音效
    def play_NG_mp3(self):
        sound_path_NG = self.text_entry_7.text()
        # 判断文件是否存在，不存在则不播放
        if os.path.exists(sound_path_NG):
            decoded_path = sound_path_NG.encode('utf-8').decode('utf-8')
            playsound(decoded_path)


    # 重写关闭函数
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', "确认退出吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            # 用过sys.exit(0)和sys.exit(app.exec_())，但没起效果
            os._exit(0)
            receive_data.close()
        else:
            event.ignore()

if __name__ == '__main__':
    from PyQt5 import QtCore
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)  # 自适应分辨率
    app = QtWidgets.QApplication(sys.argv)
    window = mywindow()
    window.show()
    sys.exit(app.exec_())