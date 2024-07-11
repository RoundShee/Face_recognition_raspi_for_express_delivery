"""
本文件夹对Qt5创建的类进行继承
"""

import sys
import cv2
import random
from threading import Thread
from PyQt5 import QtCore, QtWidgets, QtGui, Qt
from PyQt5.QtWidgets import QStackedWidget
import RoundUI.allpage
from face_Detect_Recognition_Identify import face_detection_cv2, identify_face_through_db
from InteractionDB import RoundDB


class NewMainWin(QtWidgets.QMainWindow, RoundUI.allpage.Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        RoundUI.allpage.Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # self.setWindowFlags(Qt.Qt.CustomizeWindowHint)  # 去掉标题
        self.setWindowTitle('智能快递柜系统')
        self.setFixedSize(490, 630)
        self.stackedWidget.setCurrentIndex(0)  # 0主界面 1快递员 2用户 3新用户
        self.database_rs = RoundDB()   # 实例化数据库管理
        self.label.setScaledContents(False)
        self.label_5.setScaledContents(False)
        self.label_13.setScaledContents(False)
        # 0主界面 配置
        # self.pushButton.clicked.connect(self.start_jump)
        self.video_stream = cv2.VideoCapture(0)
        self.jump_count = 0  # 跳转计时
        # self.label_22.setPixmap(QtGui.QPixmap('./resource/background.jpg'))
        # 0 主界面配置
        self.pushButton_2.clicked.connect(self.go_to_page3)
        self.pushButton.clicked.connect(self.go_to_input_code)  # 跳转取件码界面
        # 1快递员 配置
        self.pushButton_5.clicked.connect(self.back_main)
        self.pushButton_6.clicked.connect(self.tell_roundshee)
        self.pushButton_4.clicked.connect(self.go_to_drop_items)  # 投件
        self.pushButton_20.clicked.connect(self.go_to_drop_items_tests)  # 测试按钮
        self.take_item_codes = []     # 取件码存储
        # 2用户 配置
        self.id_num = None  # 暂存尊贵的用户信息 与1共用
        self.user_name = None
        self.identity = None
        self.own = None
        self.reg_date = None
        self.pushButton_10.clicked.connect(self.back_main)
        self.pushButton_9.clicked.connect(self.user_into_delete)
        self.pushButton_8.clicked.connect(self.user_get_all_items)
        self.pushButton_7.clicked.connect(self.user_get_first_items)  # 暂时一致
        # 3新用户 配置
        self.pushButton_12.clicked.connect(self.back_main)
        self.refresh_page3 = True   # 新用户录入图像是否刷新
        self.pushButton_3.clicked.connect(self.capture_to_record)
        self.user_img = None    # 暂存用户图像
        self.pushButton_13.clicked.connect(self.abort_capture)
        self.pushButton_11.clicked.connect(self.insert_new_user)
        # 4删除个人信息界面 配置
        self.pushButton_15.clicked.connect(self.back_page_2)  # 跳回用户
        self.pushButton_14.clicked.connect(self.confirm_delete_user_new)  # 再次跳转
        # 5输入取件码
        self.pushButton_16.clicked.connect(self.confirm_input_code_new)  # 取件码确认
        self.pushButton_17.clicked.connect(self.back_main)  # 取件码界面返回
        # 6投件界面
        self.pushButton_18.clicked.connect(self.back_send_win)  # 投件完成，回到快递员界面
        # 7say_bye_...
        self.pushButton_19.clicked.connect(self.back_main)

    def start_jump(self, identity, name, own):   # 用于主界面启动识别
        # self.video_stream.release()
        self.label.setText('智能快递柜系统')
        if identity == 1:  # 快递员
            self.label_11.setText('')  # 快递员界面提示清除
            self.stackedWidget.setCurrentIndex(1)
            self.label_2.setText('{}快递员，您好！'.format(name))
        else:   # 用户
            self.stackedWidget.setCurrentIndex(2)
            self.label_3.setText('尊敬的{}用户，您好！'.format(name))
            if not own:
                self.label_9.setText('您没有物品存储在柜中！')
            else:
                self.label_9.setText('您有以下物品：{}'.format(own))

    def back_main(self):    # 返回主页面
        # self.video_stream = cv2.VideoCapture(0)  # 重新绑定摄像头
        self.id_num = None  # 清空用户数据
        self.identity = None
        self.own = None
        self.reg_date = None
        self.user_name = None
        self.label_22.setText('')
        self.label.setText('Reloading')
        self.stackedWidget.setCurrentIndex(0)

    def go_to_page3(self):  # 新用户前往录入数据
        self.label.setText('智能快递柜系统')
        self.pushButton_12.setText('放弃录入 不保留任何信息')  # 更新按钮信息
        # 不需要关闭摄像头,保持打开
        self.stackedWidget.setCurrentIndex(3)
        self.label_8.setText('')

    def capture_to_record(self):    # 新用户 捕获当前帧
        ret, img = self.video_stream.read()
        self.refresh_page3 = False
        self.user_img = img

    def abort_capture(self):    # 新用户 放弃当前图像
        self.refresh_page3 = True
        self.user_img = None

    def insert_new_user(self):  # 新用户确定信息
        if self.refresh_page3:
            self.label_8.setText('请确定人脸信息！')
        elif not self.lineEdit_2.text():
            self.label_8.setText('请输入姓名！')
            print(self.lineEdit_2.text())
            print(type(self.lineEdit_2.text()))
        elif not (len(self.lineEdit.text())==11 and self.lineEdit.text().isdigit() and self.lineEdit.text()[0].isdigit()):
            self.label_8.setText('请输入正确的手机号码！')
            print(type(self.lineEdit.text()))
        else:
            result = self.database_rs.add_user(phone_num=self.lineEdit.text(), name=self.lineEdit_2.text(), cv_img=self.user_img)
            if not result:
                self.label_8.setText('录入失败！')
            else:
                self.label_8.setText('成功！感谢使用')
                self.refresh_page3 = True
                self.user_img = None
                self.lineEdit.setText('')
                self.lineEdit_2.setText('')
                self.pushButton_12.setText('返回：立即使用')

    def user_into_delete(self):  # 用户删除自身信息  绑定push_button_9
        if self.own:
            self.label_16.setText('请取出所有快递再进行操作！')
        else:
            self.pushButton_15.setText('取消')
            self.label_16.setText('')
            self.label_10.setText('尊敬的{}用户,感谢您使用本产品！'.format(self.user_name))
            self.label_12.setText('注册时间：{}  感谢陪伴  '.format(self.reg_date))
            self.label_15.setText('')
            # 加载面部信息
            frame = cv2.imread('./resource/sets/user'+self.id_num+'/user'+self.id_num+'.jpg')
            if frame.shape[1] / frame.shape[0] > self.label_13.width() / self.label_13.height():  # 原图较长 长边撑满
                width = self.label_13.width()
                height = int(frame.shape[0] * (width / frame.shape[1]))
            else:  # 原图较高， 高度撑满
                height = self.label_13.height()  # 调整尺寸
                width = int(frame.shape[1] * (height / frame.shape[0]))
            frame = cv2.resize(frame, (width, height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.Qframe = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1] * 3,
                                       QtGui.QImage.Format_RGB888)
            self.label_13.setPixmap(QtGui.QPixmap.fromImage(self.Qframe))
            self.lineEdit_3.setText('{}xxxx'.format(self.id_num[0:7]))
            self.update()
            self.stackedWidget.setCurrentIndex(4)   # 进入删除页面

    def confirm_delete_user(self):  # 按下确认按钮删除个人信息
        if self.lineEdit_3.text() == self.id_num:  # 删除成功
            self.database_rs.remove_user_by_phone(self.id_num)
            self.label_15.setText('删除成功！')
            self.label_13.setText('Error:FileNorFound')
            self.label_12.setText('来日方长，后会有期！')
            self.label_10.setText('感谢使用：')
            self.pushButton_15.setText('返回')
        else:
            self.label_15.setText('输入错误！')
            self.lineEdit_3.setText('{}xxxx'.format(self.id_num[0:7]))

    def confirm_delete_user_new(self):  # fuck this
        if self.lineEdit_3.text() == self.id_num:  # 删除成功
            self.database_rs.remove_user_by_phone(self.id_num)
            self.stackedWidget.setCurrentIndex(7)
        else:
            self.label_15.setText('输入错误！')
            self.lineEdit_3.setText('{}xxxx'.format(self.id_num[0:7]))

    def tell_roundshee(self):  # 快递员联系管理员界面
        self.label_11.setText('联系作者RoundShee')
        self.own = None
        self.update()  # 需要吗?

    def user_get_all_items(self):  # 用户取件
        self.database_rs.update_user_items(self.id_num)
        self.own = None
        self.label_16.setText('')
        self.label_9.setText('您没有物品存储在柜中！')

    def go_to_input_code(self):  # 跳转到取件码取件界面
        self.lineEdit_4.setText('')  # 清空输入框
        self.label_18.setText('')   # 清空错误提示
        self.stackedWidget.setCurrentIndex(5)  # 跳转

    def confirm_input_code(self):  # 取件码确认判断
        user_input_code = self.lineEdit_4.text()  # 获取输入
        name, identity, own, date = self.database_rs.get_information_by_phone(user_input_code)
        if name and own:  # 确有此人,直接跳转
            self.id_num = user_input_code
            self.user_name = name
            self.identity = identity
            self.own = own
            self.reg_date = date
            self.start_jump(identity, name, own)  # 还是到了用户界面
        else:
            self.label_18.setText('取件码无效!')

    def confirm_input_code_new(self):  # 随机取件码判断
        user_input_code = self.lineEdit_4.text()  # 获取输入
        code_result = 0  # 错误
        for code_haved in self.take_item_codes:
            if code_haved == user_input_code:
                code_result = 1
                self.take_item_codes.remove(code_haved)
        if code_result:
            self.label_18.setText('取件成功!')
        else:
            self.label_18.setText('取件码无效!')

    def back_page_2(self):
        self.stackedWidget.setCurrentIndex(2)

    def user_get_first_items(self):  # 取件一个
        if not self.own:    # 空串
            pass
        elif len(self.own) == 2:  # 清空
            self.own = None
            self.label_9.setText('您没有物品存储在柜中！')
            self.label_16.setText('')
            self.database_rs.update_user_items(self.id_num, None)
        else:
            self.own = self.own[3:]
            print(self.own)
            self.label_9.setText('您有以下物品：{}'.format(self.own))
            self.label_16.setText('')
            self.database_rs.update_user_items(self.id_num, self.own)

    def go_to_drop_items(self):  # 跳转投件界面的按钮
        abc = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
        new_code = random.choice(abc)+random.choice(abc)+random.choice(abc)+random.choice(abc)
        if len(self.take_item_codes):   # 空
            self.take_item_codes.append(new_code)  # 添加到缓存区
        else:   # 保证取件码不重复
            take_in = 1
            for code in self.take_item_codes:
                if code == new_code:
                    take_in = 0
            if take_in:
                self.take_item_codes.append(new_code)
        self.label_21.setText('生成取件码：{}'.format(new_code))
        self.label_19.setText('门已开,快递员{},请投件'.format(self.user_name))
        self.stackedWidget.setCurrentIndex(6)  # 跳转到投件界面

    def go_to_drop_items_tests(self):  # 投件给张嘉铭
        try:
            test_user_num = 'My num is secret'
            name, identity, own, date = self.database_rs.get_information_by_phone(test_user_num)
            if own:  # 有件
                own = own+','+random.choice('ABCDEF')+random.choice('123456789')
            else:   # 没件
                own = random.choice('ABCDEF')+random.choice('123456789')
            self.database_rs.update_user_items(test_user_num, own)
            self.label_11.setText('[测试]向用户[张嘉铭]投件{}成功！'.format(own[-2:]))
        except Exception:
            print('投件失败!')
            self.label_11.setText('指定用户不存在或投件失败！')
        # finally:
        #     # self.stackedWidget.setCurrentIndex(1)

    def back_send_win(self):  # 设定向某用户发送快递，完成跳转
        self.label_11.setText('')
        self.stackedWidget.setCurrentIndex(1)

    def paintEvent(self, a0: QtGui.QPaintEvent):
        if self.stackedWidget.currentIndex() == 0:  # 主页刷新
            ret, frame, result = face_detection_cv2(self.video_stream)  # 检测人脸
            if ret:  # 正确配置摄像头的情况下输出视频
                if frame.shape[1]/frame.shape[0] > self.label.width()/self.label.height():  # 原图较长 长边撑满
                    width = self.label.width()
                    height = int(frame.shape[0] * (width / frame.shape[1]))
                else:  # 原图较高， 高度撑满
                    height = self.label.height()    # 调整尺寸
                    width = int(frame.shape[1] * (height / frame.shape[0]))
                frame = cv2.resize(frame, (width, height))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.Qframe = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QtGui.QImage.Format_RGB888)
                # print('这是shape(1)={},  shape(0)={}'.format(frame.shape[1], frame.shape[0]))  # shape(0)高 shape(1)宽
                self.label.setPixmap(QtGui.QPixmap.fromImage(self.Qframe))
                self.update()
                if self.jump_count < 60:  # 控制识别速度
                    if self.jump_count > 35:
                        self.label_22.setText('')   # 清空
                    self.jump_count += 1
                    id_num = None
                else:   # 识别
                    self.jump_count = 0
                    id_num = identify_face_through_db(frame)  # 识别到在系统的用户直接返回获取信息
                    if id_num:  # 识别到尊贵的用户
                        name, identity, own, date = self.database_rs.get_information_by_phone(id_num)
                        self.id_num = id_num
                        self.user_name = name
                        self.identity = identity
                        self.own = own
                        self.reg_date = date
                        self.start_jump(identity, name, own)
                    elif result:
                        self.label_22.setText('新用户，请录入人脸信息！')
            else:
                self.label.setText('智能快递柜系统')
                self.update()
        if self.stackedWidget.currentIndex() == 3:  # 主页刷新
            ret, frame, result = face_detection_cv2(self.video_stream)  # 检测人脸
            if ret:
                if self.refresh_page3:  # 正确配置摄像头且正常使用情况下输出视频
                    if frame.shape[1] / frame.shape[0] > self.label_5.width() / self.label_5.height():  # 原图较长 长边撑满
                        width = self.label_5.width()
                        height = int(frame.shape[0] * (width / frame.shape[1]))
                    else:  # 原图较高， 高度撑满
                        height = self.label_5.height()  # 调整尺寸
                        width = int(frame.shape[1] * (height / frame.shape[0]))
                    frame = cv2.resize(frame, (width, height))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.Qframe = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QtGui.QImage.Format_RGB888)
                    self.label_5.setPixmap(QtGui.QPixmap.fromImage(self.Qframe))
                    self.update()
                else:
                    frame = cv2.cvtColor(self.user_img, cv2.COLOR_BGR2RGB)
                    if frame.shape[1] / frame.shape[0] > self.label_5.width() / self.label_5.height():  # 原图较长 长边撑满
                        width = self.label_5.width()
                        height = int(frame.shape[0] * (width / frame.shape[1]))
                    else:  # 原图较高， 高度撑满
                        height = self.label_5.height()  # 调整尺寸
                        width = int(frame.shape[1] * (height / frame.shape[0]))
                    frame = cv2.resize(frame, (width, height))
                    self.Qframe = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1] * 3,
                                               QtGui.QImage.Format_RGB888)
                    self.label_5.setPixmap(QtGui.QPixmap.fromImage(self.Qframe))
                    self.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = NewMainWin()
    ui.show()
    sys.exit(app.exec_())


