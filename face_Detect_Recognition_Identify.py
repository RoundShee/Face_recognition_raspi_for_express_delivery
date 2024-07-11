"""
本文档接出face_recognition的各种用法
"""

import face_recognition
import cv2
from PIL import Image, ImageDraw
import numpy as np
import os
import pickle

faceCascade = cv2.CascadeClassifier('resource/haarcascade_frontalface_default.xml')


# 仅使用cv2 参考github-Face-Recognition-using-Raspberry-Pi-master
def face_detection_cv2(cap=None):
    """
    仅使用cv2 画锚框
    :param cap:
    :return:
    """
    if cap is None:
        cap = cv2.VideoCapture(0)  # 设置摄像头
    ret, img = cap.read()
    if ret:
        img = cv2.flip(img, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(20, 20)
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # roi_gray = gray[y:y + h, x:x + w]
            # roi_color = img[y:y + h, x:x + w]
        # cv2.imshow('video', img)
    else:   # 无法获取摄像头帧时返回正确变量格式
        ret = 0
        img = None
        faces = []
    return ret, img, len(faces)


def identify_face_through_db(img):
    """
    仍根据传入图像对比数据库，根据数据库处理结果返回特定数据
    :param img:
    :return:
    """
    # 加载数据
    all_files = os.listdir('./resource/sets')
    known_face_id = []
    known_face_encodings = []
    for filename in all_files:
        known_face_id.append(filename[4:])
        filename_next = filename + '.encoded'
        fd = open('./resource/sets/'+filename+'/'+filename_next, "rb")
        temp = pickle.load(fd)
        known_face_encodings.append(temp[0])
        fd.close()
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            return known_face_id[best_match_index]
        else:
            return None

