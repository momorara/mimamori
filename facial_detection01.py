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
2022/05/29  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)で
            cv2.error: OpenCV(4.1.0) のエラーが出るので、パスする
2022/05/31  いい感じの写真を選ぶため、顔の大きさ、中心に近い顔を考慮した。
2022/06/01  fileによる関数は使わないので削除
    01
2022/06/04  detectMultiScaleのパラメータを変えてみる
2022/06/09  リリース


"""
import cv2
import configparser
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


# 指定されたフレームsから顔検出 顔があったら、ファィルにして帰る
# よりいい感じの写真を選ぶため　顔の大きさ、中心にあるを考慮
def facial_detection_frame(frames):
    height, width, channels = frames[0].shape[:3]
    i = 0
    face = 0
    frame_n = [0]*100
    for frame in frames:
        # convert the input frame from (1) BGR to grayscale (for face detection)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(gray, scaleFactor=1.11, 
            minNeighbors=6, minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE)
        # 顔認識が出来た時はその時のframeと1を返す
        if len(rects) == 1:
            face = face + 1
            # 顔の有る無し
            frame_n[i] = 1
            if face_box == 1:
                # 顔検出のボックスを描く Bounding box
                boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
                # print(boxes)
                for (top, right, bottom, left) in boxes:
                    # Bounding boxの大きさは正方形なので、高さのみで表現
                    face_size = bottom - top
                    # draw the predicted face name on the image - color is in BGR
                    # print(top, right, bottom, left)
                    cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 225), 2) #イエロー

                    # 顔検出の大きさでバウンテイボックの色を変える
                    # if face_size <30:
                    #     cv2.rectangle(frame, (left, top), (right, bottom),(255, 0, 0), 2) #ブルー
                    # else:
                    #     if face_size <60:
                    #         cv2.rectangle(frame, (left, top), (right, bottom),(0, 225, 0), 2) #グリーン
                    #     else:
                    #         if face_size <90:
                    #             cv2.rectangle(frame, (left, top), (right, bottom),(0, 0, 255), 2) #レッド
                    #         else:
                    #             cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 225), 2) #イエロー
                    #         """
                    #         https://www.rapidtables.org/ja/web/color/RGB_Color.html
                    #         ブラック    #000000	(0,0,0)
                    #         白い	    #FFFFFF (255,255,255)
                    #         赤	        #FF0000	(0, 0, 255)
                    #         緑	        #00FF00	(0,0,255)
                    #         青い	    #0000FF	(255,0,0)
                    #         黄	        #FFFF00	(255,255,0)
                    #         水色	    #00FFFF	(0,255,255)
                    #         ピンク  	#FF00FF	(255,0,255)
                    #         https://itsakura.com/html-color-codes
                    #         """

                    # 画像に時刻を挿入
                    dt_now = datetime.datetime.now()
                    dt_str = dt_now.strftime('%Y/%m/%d %H:%M:%S') + ' face'
                    cv2.putText(frame, dt_str,(0,height-5), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 2, cv2.LINE_AA)
                    cv2.imwrite('test.jpg',frame)

                # 顔の大きさ
                frame_n[i] = frame_n[i] * face_size
                # 顔が中心に近い
                frame_n[i] = int(frame_n[i] * (height/2 - abs(height/2 - (top + bottom)/2)))
                frame_n[i] = int(frame_n[i] * (width /2 - abs(width/ 2 - (right + left)/2)))

                # 顔のサイズが小さい場合は、顔検出を採用しない
                if face_size < 40 :
                    frame_n[i] = 0
                    face = face - 1
        else:
            frame_n[i] = 0
        i = i + 1
    if face > 0:
        # 顔があった場合
        face_max     = max(frame_n)              # 差の最大値
        face_index   = frame_n.index(face_max)
        print('face',face,'face_max',face_max,'face_index',face_index,'\n','frame_n',frame_n)
        return frames[face_index],1
        
    else:# 顔無
        return frame,-1 # 見つからなかったら-1を返す

def main():
    files =['image-1.jpg','image-2.jpg','image.jpg','image-1.jpg','image-2.jpg','image.jpg']
    files =['movie1.jpg','movie3.jpg','movie5.jpg','movie7.jpg','movie8.jpg','movie9.jpg']
    files =['test2.jpg','test5.jpg','test7.jpg','test8.jpg','test16.jpg','test15.jpg','test14.jpg','test13.jpg','test9.jpg','test10.jpg','test11.jpg','test12.jpg']
    files =['movie9.jpg']
    files =['result0.jpg','result1.jpg','result2.jpg','result3.jpg','result4.jpg','result5.jpg','result6.jpg','result7.jpg','result8.jpg','result9.jpg']
    frames = []
    print(files)
    for file in files:
        frame = cv2.imread(file)  
        frames.append(frame)
    result_frame,no = facial_detection_frame(frames)
    print('result_frame,no',result_frame,no)


if __name__ == '__main__':
    main()
