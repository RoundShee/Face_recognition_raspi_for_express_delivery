"""
数据交互部分
"""

import os
import shutil
import sqlite3
import cv2
import face_recognition
import pickle


class RoundDB:
    def __init__(self):
        self.database = './resource/database.db'    # 数据库文件路径
        self.sets = './resource/sets'   # 每个用户资源存储路径
        self.users_count = 0
        conn = sqlite3.connect(self.database)   # 没有会自动创建
        cursor = conn.cursor()

        try:
            # 检测人脸数据目录是否存在，不存在则创建
            if not os.path.isdir(self.sets):
                os.makedirs(self.sets)
            # 查询数据表是否存在，不存在则创建
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                              user_id VARCHAR(11) PRIMARY KEY NOT NULL,
                              name TEXT NOT NULL,
                              identity int,
                              own TEXT,
                              created_time DATE DEFAULT (date('now','localtime'))
                              )
                          ''')      # 手机号 姓名 身份 own哪个格子有快递 创建时间
            # 查询数据表记录数
            cursor.execute('SELECT Count(*) FROM users')
            result = cursor.fetchone()
            self.users_count = result[0]
        except Exception as e:
            # logging.error('读取数据库异常，无法完成数据库初始化')
            # self.isDbReady = False
            # self.initDbButton.setIcon(QIcon('./icons/error.png'))
            # self.logQueue.put('Error：初始化数据库失败')
            print('读取数据库异常，无法完成数据库初始化')
        # else:
        #     self.isDbReady = True
        #     self.dbUserCountLcdNum.display(dbUserCount)
        #     self.logQueue.put('Success：数据库初始化完成')
        #     self.initDbButton.setIcon(QIcon('./icons/success.png'))
        #     self.initDbButton.setEnabled(False)
        #     self.addOrUpdateUserInfoButton.setEnabled(True)
        finally:
            cursor.close()
            conn.commit()
            conn.close()

    def add_user(self, phone_num, name, identity=0, cv_img=None):
        """
        增加用户到数据库,仅数据库,需要人脸再需其他方法
        :param cv_img: opencv传入图像frame
        :param phone_num:
        :param name:
        :param identity:
        :return:
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        return_value = 0  # 向外界表明本次写入失败 1成功
        try:
            cursor.execute('SELECT * FROM users WHERE user_id=?', (phone_num,))
            if cursor.fetchall():
                text = '数据库：手机号为{}已被占用,选择认证后更新面部信息或联系管理员'.format(phone_num)
                print(text)
            else:
                # 插入新记录
                cursor.execute('INSERT INTO users (user_id, name, identity) VALUES (?, ?, ?)',
                               (phone_num, name, identity,))
                if not os.path.exists('{}/user{}'.format(self.sets, phone_num)):
                    os.makedirs('{}/user{}'.format(self.sets, phone_num))   # 建立人脸文件夹
                cv2.imwrite('{0}/user{1}/user{1}.jpg'.format(self.sets, phone_num), cv_img)
                face_locations = face_recognition.face_locations(cv_img)
                face_encodings = face_recognition.face_encodings(cv_img, face_locations)
                f = open('{0}/user{1}/user{1}.encoded'.format(self.sets, phone_num), 'wb')
                pickle.dump(face_encodings, f)
                f.close()
                return_value = 1
            cursor.execute('SELECT Count(*) FROM users')
            result = cursor.fetchone()
            self.users_count = result[0]
        except Exception:
            print('读写数据库异常，无法向数据库插入/更新记录')
        finally:
            cursor.close()
            conn.commit()
            conn.close()
        return return_value

    def get_information_by_phone(self, phone_num):
        """
        通过手机号获取当前所有信息
        :param phone_num:
        :return: name, identity, own, date
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users WHERE user_id=?', (phone_num,))
            ret = cursor.fetchall()
            if not ret:
                name_ret = None
                identity_ret = None
                own_ret = None
                date_ret = None
            else:
                name_ret = ret[0][1]
                identity_ret = ret[0][2]
                own_ret = ret[0][3]
                date_ret = ret[0][4]
        except Exception:
            print('读写数据库异常，无法向数据库插入/更新记录')
            name_ret, identity_ret, own_ret, date_ret = None, None, None, None
        else:
            pass
        finally:
            cursor.close()
            conn.close()
        return name_ret, identity_ret, own_ret, date_ret

    def remove_user_by_phone(self, phone_num):
        """
        删除用户信息以及人脸数据
        :param phone_num:
        :return:
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM users WHERE user_id=?', (phone_num,))
        except Exception:
            cursor.close()
            print('无法从数据库中删除{}'.format(phone_num))
        else:
            cursor.close()
            conn.commit()
            if os.path.exists('{}/user{}'.format(self.sets, phone_num)):
                try:
                    shutil.rmtree('{}/user{}'.format(self.sets, phone_num))
                except Exception:
                    print('系统无法删除删除{}/user{}'.format(self.sets, phone_num))
            else:
                print('未找到{}的人脸信息'.format(phone_num))
            print('已成功删除{}用户记录。'.format(phone_num))
        finally:
            conn.close()

    def update_user_items(self, phone_num, items=None):
        """
        更新用户物品
        :return:
        """
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users set own=? WHERE user_id=?', (items, phone_num))
        except Exception:
            cursor.close()
            print('更新失败{}'.format(phone_num))
        else:
            cursor.close()
            conn.commit()

