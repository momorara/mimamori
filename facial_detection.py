#! /usr/bin/python
"""
2022/04/16    顔認識の結果をcsv保存する
    01      同じ顔でも連続して記録する
            face_recognitionパッケージの別モジュールを使い
2022/04/19    ファイル名を起動時の日付をファイル名にする。
    011
2022/05/02    認識の程度を数値化する
    02      
    021        数値をまとめる表示、保存

facial_detection
    03      顔認識に特化 ファィル形式の入力で顔を判別できたら 1 出来なかったら 0
            入力にファィル名、で顔認識できたらそのファィル名と番号
            できなかったら no_faceを返す
    04      顔検出したばあいにface_boxを描く
"""

import configparser
import cv2
import os
import datetime
import getpass

# ユーザー名を取得
dt_now = datetime.datetime.now()
print(dt_now)
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/mimamori/' # cronで起動する際には絶対パスが必要

# config,iniから値取得
# --------------------------------------------------
# configparserの宣言とiniファイルの読み込み
config_ini = configparser.ConfigParser()
config_ini.read(path + 'config.ini', encoding='utf-8')
# --------------------------------------------------
# camera使用複数写真対応:2 camera使用:1 camera不使用:0
camera = int(config_ini.get('DEFAULT', 'camera'))
face_box = int(config_ini.get('DEFAULT', 'face_box'))

#use this xml file
cascade = "haarcascade_frontalface_default.xml"
# cascade = "haarcascade_upperbody.xml"
# cascade = "haarcascade_fullbody.xml"
detector = cv2.CascadeClassifier(cascade)

# 指定されたファィルのリストから顔進出
def facial_detection(files):
    # print('facial_detection start')
    i = 0
    for file in files:
        # ファイルから読み取りする
        frame = cv2.imread(file)  
        # convert the input frame from (1) BGR to grayscale (for face detection)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
            minNeighbors=5, minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE)
        # 顔認識が出来た時は lenが1となり、その時のファィル名と番号を返す
        # print(len(rects))
        if len(rects) == 1:
            if face_box == 1:
                # 顔検出のボックスを描く
                boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
                # print(boxes)
                for (top, right, bottom, left) in boxes:
                    # draw the predicted face name on the image - color is in BGR
                    # print(top, right, bottom, left)
                    cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 225), 2)
                # cv2.imwrite('box.jpg', frame)
                os.remove(file)
                cv2.imwrite(file, frame)
            return file,i
        i = i +1
    return 'no_face',-1

# 指定されたフレームから顔検出 顔があったら、ファィルにして帰る
def facial_detection_frame(frame):
    # convert the input frame from (1) BGR to grayscale (for face detection)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # detect faces in the grayscale frame
    rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
        minNeighbors=5, minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE)
    # 顔認識が出来た時は lenが1となり、その時のファィル名と番号を返す
    # print(len(rects))
    try:
        os.remove('image.jpg')
    except:
        pass
    if len(rects) == 1:
        if face_box == 1:
            
            # 顔検出のボックスを描く
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
            # print(boxes)
            for (top, right, bottom, left) in boxes:
                # draw the predicted face name on the image - color is in BGR
                # print(top, right, bottom, left)
                cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 225), 2)           
            
            # 顔があったら、ファィルにして帰る
            cv2.imwrite('image.jpg', frame)

        return frame,1
    cv2.imwrite('image.jpg', frame)
    return frame,-1

def main():
    files =['image-1.jpg','image-2.jpg','image.jpg','image-1.jpg','image-2.jpg','image.jpg']
    files =['movie1.jpg','movie3.jpg','movie5.jpg','movie7.jpg','movie8.jpg','movie9.jpg']
    result,no = facial_detection(files)
    print(result,no)


if __name__ == '__main__':
    main()
