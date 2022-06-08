#! /usr/bin/python
"""
2022/04/16	顔認識の結果をcsv保存する
    01      同じ顔でも連続して記録する
            face_recognitionパッケージの別モジュールを使い
    02      認識の程度を数値化する
	021		数値化を見える化

2022/05/25	カメラ画像を取りながらトリガー信号の前後を切り出して記録ができる。
			ドラレコのような機能を実装したい。
			トリガーの前10秒後20秒とか
2022/05/26  関数化、トリガー対応
    01
2022/05/28  フレーム間の差分を試してみる
2022/05/29  最初のフレームとの差をcv2で計算して、最大のものを選ぶ
    02      1. mainからのファィルキックで、ドラレコ記録を行う。file名:image_get.txtがあるか無いか
            2. 記録フレームに対して、顔検出をしてできれば、image.jpgを作る
            3. 記録フレームに対して、差分計算して最大値のフレームでimage.jpgを作る
            4. jpegできなければ、記録フレームの中間フレームでimage.jpgを作る
            5. mainがimage.jpgを添付して通知する。
2022/05/30  ファイル起動実装
    03
2022/05/31  トリミング差分最大実装
            ・差分最大が一番いい感じの写真とは限らない
            　  トリミングしてもう一度差分最大を取ると、画像中心部に映っている可能性が高くなる。
                トリミングするにはopencvでデータを取り込む必要がありました。
            ・顔検出した場合
　              より大きい顔、より中心に近い顔　が良いのかな
2022/06/02  修正
    032
2022/06/04  たまに原因不明で落ちていることがあるので、rebornを実装。
            実際はmimqmoriで、driveRecodeを起動します。
2022/06/07  顔検出失敗した場合、左右に20度傾けてやってみる
2022/06/09  リリース




最終版では、sw起動を削除すること
"""
import RPi.GPIO as GPIO
import time
import os
import copy
import datetime
import cv2
from imutils.video import FPS
import facial_detection01
import getpass
import numpy as np
from math import ceil

# from xml.sax.handler import feature_namespace_prefixes

# ユーザー名を取得
dt_now = datetime.datetime.now()
print(dt_now)
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/mimamori/' # cronで起動する際には絶対パスが必要
print(path)
camera_jpg = path + 'image.jpg'

# cronで起動するとカレントディレクトリはルートになるので、
# プログラムのあるディレクトリに移動する
print('dirname:', os.path.dirname(__file__))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

###################log print#####################
# 自身のプログラム名からログファイル名を作る
import sys
args = sys.argv
logFileName = args[0].strip(".py") + "_log.csv"
print(logFileName)
# ログファイルにプログラム起動時間を記録
import csv
# 日本語文字化けするので、Shift_jisやめてみた。
f = open(logFileName, 'a')
csvWriter = csv.writer(f)
csvWriter.writerow([datetime.datetime.now(),'  program start!!'])
f.close()
#----------------------------------------------
def log_print(msg1="",msg2="",msg3=""):
    # エラーメッセージなどをプリントする際に、ログファイルも作る
    # ３つまでのデータに対応
    print(msg1,msg2,msg3)
    # f = open(logFileName, 'a',encoding="Shift_jis") 
    # 日本語文字化けするので、Shift_jisやめてみた。
    f = open(logFileName, 'a')
    csvWriter = csv.writer(f)
    csvWriter.writerow([datetime.datetime.now(),msg1,msg2,msg3])
    f.close()
################################################

# SW
sw   = 6
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(sw,GPIO.IN)
def Read_sw():
    if GPIO.input(sw):return 'on'
    return 'off'


print('please wait few minuts')

#use this xml file
cascade = "haarcascade_frontalface_default.xml"
detector = cv2.CascadeClassifier(cascade)


def image_diff(frames):
    # 与えられたフレームの最初と他の差を数値で返します。
    frame_diff = [0]
    #グレースケース変換
    gray_frame_0 = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
    for i in range(len(frames)-1):
        #グレースケース変換
        gray_frame_i = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY)
        #単純に画像の引き算
        img_diff = cv2.absdiff(gray_frame_0, gray_frame_i)
        #差分画像の２値化（閾値が50）
        ret, img_bin = cv2.threshold(img_diff, 50, 255, 0)
        # print('img_bin',sum(sum(img_bin)))
        result = sum(sum(img_bin))
        frame_diff.append(result)
    
    diff_max     = max(frame_diff)              # 差の最大値
    diff_index   = frame_diff.index(diff_max)   # 差の最大値のあるフレーム インデックス
    if diff_index == 0:                         # もし最大値が和の場合は、フレームの中間位とする。
        diff_index = 30
    result_frame = frames[diff_index]           # 差の最大値のあるフレーム 画像
    diff_sum = sum(frame_diff)                  # 差の合計
    return result_frame, diff_index, diff_max ,diff_sum


# ドラレコのようにトリガーが有った時から過去の画像とそのあとを記録する。
# movie_time_sec :画像の記録秒数
# past_time_sec  :過去の記録の秒数
# movie_fps      :一秒の画像枚数
def getMovieFrames(movie_time_sec, past_time_sec, movie_fps):

    # 引数から総フレーム数を算出
    total_frames = movie_time_sec * movie_fps
    # 引数から残す過去フレーム数を算出
    past_frames  = past_time_sec  * movie_fps
    # fpsに合ったディレイ時間の算出 1step=10msなので、
    frame_deley_time_n = int((1 / movie_fps) * 0.8 *1000 /10)
    frame_deley_time   = (1/movie_fps)*0.9
    # print(frame_deley_time_n)
    # print(total_frames, past_frames)
    
    # トリミングするにはopencvでデータを取り込む必要がありました。
    cap = cv2.VideoCapture(0)
    fps = FPS().start() # start the FPS counter
    frame_n = 1
    frames  = []
    frames.clear()
    trigger = 'off'
    while True:
        # カメラから1フレーム取り込みリストに追加
        ret, frame = cap.read()
        frames.append(frame)

        frame_n = frame_n +1
        # 指定フレームを超えたら 前方del_frames分を削除
        if frame_n > total_frames:
            if trigger == 'on':
                break # トリガーが有って、必要フレーム取り込んだら次のステップへ
            del frames[:(len(frames)-past_frames)]
            frame_n = frame_n - len(frames) -past_frames

        # update the FPS counter
        fps.update()

        # 録画中の画像確認　運用ではいらないかな
        # cv2.imshow("Recording", frames[len(frames)-1])
        # cv2.waitKey(1)

        # fpsに合ったディレイを作る
        start = time.time()
        parst = time.time()
        i = 0
        while parst-start < frame_deley_time:
            time.sleep(0.01)
            # トリガーを確認 0.01s*20 = 0.2秒毎にファイルの有無を確認
            if i > 20:
                #　ファイルがあるか無いかを確認する。
                if os.path.exists('image_get.txt'):
                    # ファイルがあれば、ドラレコ起動
                    trigger = 'on'
                    # 必要な過去を残す
                    if len(frames) > past_frames:
                        del frames[:(len(frames) -past_frames)]
                    frame_n = frame_n - len(frames) -past_frames
                    os.remove('image_get.txt') #ファイルを削除
                    break 
                i = 0
            i = i +1

            # # 仮のトリガーとしてswを確認 リリース時にコメントアウト？
            # # print(Read_sw(),trigger)
            # if Read_sw() == 'on' and trigger == 'off':
            #     trigger = 'on'
            #     # 必要な過去を残す
            #     if len(frames) > past_frames:
            #         del frames[:(len(frames) -past_frames)]
            #     frame_n = frame_n - len(frames) -past_frames
            #     break 


            parst = time.time()            

    # stop the timer and display FPS information
    fps.stop()
    # vs.stop()
    cap.release()

    print("[INFO] elasped time:  {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS :   {:.2f}".format(fps.fps()))
    print("[INFO] frame n     :  {:.2f}".format(len(frames)))
    cv2.destroyAllWindows()
    return frames


# 画像frameを受け取り傾けたフレームを作り返す
def image_angle(frames,angle):
    # 作業フレームを作る
    frames_angle = copy.copy(frames)
    # 縦横サイズ取得
    org_width  = frames_angle[0].shape[1]
    org_height = frames_angle[0].shape[0]
    # log_print(org_width,org_height,big_size)
    # 回転させたい角度
    # angle  一応　20度(右)  か  -20度(左)
    angle = angle * -1
    # 拡大比率
    scale = 1.0

    i = 0
    for frame in frames_angle:

        # 拡大画像の作成
        big_img = np.zeros((org_height * 2, org_width * 2 ,3), np.uint8)
        big_img[ceil(org_height/2.0):ceil(org_height/2.0 *3.0), ceil(org_width/2.0):ceil(org_width/2.0 *3.0)] = frame
        # 画像の中心位置
        center = tuple(np.array([big_img.shape[1] * 0.5, big_img.shape[0] * 0.5]))
        # 画像サイズの取得(横, 縦)
        size   = tuple(np.array([big_img.shape[1], big_img.shape[0]]))
        # 回転変換行列の算出
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
        # アフィン変換
        frames_angle[i] = cv2.warpAffine(big_img, rotation_matrix, size, flags=cv2.INTER_CUBIC)

        # # 確認用に保存します。
        # filename= 'result' + str(i) + '.jpg'
        # cv2.imwrite(filename,frames_angle[i])
        i = i + 1

    return frames_angle

def main():

    movie_time_sec, past_time_sec, movie_fps = 10, 4, 4
    while True:
        # 動画フレームを取得
        print()
        log_print('動画フレームを取得')
        frames =[]
        frames.clear()
        frames = getMovieFrames(movie_time_sec, past_time_sec, movie_fps)

        # 動画フレームを再生
        # print('動画フレームを再生')
        # for i in range(len(frames)):
        #     # print(i)
        #     cv2.imshow("playback", frames[i])
        #     cv2.waitKey(1) 
        #     time.sleep(0.4)
        # cv2.destroyAllWindows()

        # framesを顔検出
        log_print('framesを顔検出')
        result_frame,no = facial_detection01.facial_detection_frame(frames)
        if no == 1:
            print('顔検出 成功')
            # mimamoriに渡すファィルを保存
            cv2.imwrite('image.jpg',result_frame)
        else:
            print('顔検出 傾けてトライ')
            # 画像を傾けて顔検出
            frames_angles = image_angle(frames,-20)
            result_frame,no = facial_detection01.facial_detection_frame(frames_angles)
            if no == 1:
                print('顔検出 成功 angle')
                # mimamoriに渡すファィルを保存
                cv2.imwrite('image.jpg',result_frame)
            else:
                # 画像を傾けて顔検出
                frames_angles = image_angle(frames,20)
                result_frame,no = facial_detection01.facial_detection_frame(frames_angles)
                if no == 1:
                    print('顔検出 成功 angle')
                    # mimamoriに渡すファィルを保存
                    cv2.imwrite('image.jpg',result_frame)


        if no == -1 :
            print('顔検出 失敗')
            # 顔認識できなかった場合

            # frameの差分を画像処理で計算
            log_print('frameの差分を画像処理で計算')
            result_frame_1, diff_index_1, diff_max_1 ,diff_sum_1 = image_diff(frames)
            # 画像の大きさを取得
            height, width, channels = result_frame_1.shape[:3]

            print('diff_max',diff_max_1,' diff_index',diff_index_1)
            # mimamoriに渡すファィルを保存 取り敢えずの差分最大画像
            if no == -1 :
                # 画像に時刻を挿入
                dt_now = datetime.datetime.now()
                dt_str = dt_now.strftime('%Y/%m/%d %H:%M:%S') + ' diff1'
                cv2.putText(result_frame_1, dt_str,(0,height-5), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 2, cv2.LINE_AA)
                cv2.imwrite('image.jpg',result_frame_1)

            # トリミング差分
            frames_tri = copy.copy(frames)
            # print("width: " + str(width))
            # print("height: " + str(height))

            # トリミング
            for i in range(len(frames_tri)):
                frames_tri[i] = frames_tri[i][int(height/4):int(height*3/4),int(width/4):int(width*3/4)]
            # frameの差分を画像処理で計算
            result_frame_2, diff_index_2, diff_max_2, diff_sum_2 = image_diff(frames_tri)
            # 差分の合計が0でなければ、差分最大のフレームを採用
            if diff_sum_2 != 0:
                # トリミングの差分最大indexが、差分最大のプラスマイナス 5 フレーム以内にあること
                if (diff_index_2 > diff_index_1 - 5) and (diff_index_2 < diff_index_1 + 5): 
                    # よりいい感じの画像と考えられる差分最大画僧
                    if no == -1 :
                        # 画像に時刻を挿入
                        dt_now = datetime.datetime.now()
                        dt_str = dt_now.strftime('%Y/%m/%d %H:%M:%S') + ' diff2'
                        cv2.putText(frames[diff_index_2], dt_str,(0,height-5), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 2, cv2.LINE_AA)
                        cv2.imwrite('image.jpg',frames[diff_index_2])

            # print(diff_sum_2, diff_index_2, diff_index_1)


        # # リリース時はコメントアウトする。
        # # ここで結果の検証用にframesをファイルとして落としておくと良い
        # # ファイル名を作る
        # # 日付のファィル名を作る
        # dt_now = datetime.datetime.now()
        # day_0 = ''
        # if dt_now.day < 10 :
        #     day_0   = '0'
        # fileName = './jpg/' + day_0 + str(dt_now.day) + '-' + str(dt_now.hour) + str(dt_now.minute) 
        # # jpgディレクトリに保存
        # for i in range(len(frames)):
        #     fileName_1 = fileName + '-' + str(i) + '.jpg'
        #     cv2.imwrite(fileName_1,frames[i])
        
        # # 顔検出の結果
        # fileName_2 = fileName + '-' + 'face' + '.jpg'
        # cv2.imwrite(fileName_2,result_frame)

        # try:
        #     # 差分の結果
        #     fileName_2 = fileName + '-' + 'deff-0' + '.jpg'
        #     cv2.imwrite(fileName_2,result_frame_1)
        #     # 差分　いい感じの結果
        #     fileName_2 = fileName + '-' + 'deff-1' + '.jpg'
        #     cv2.imwrite(fileName_2,result_frame_2)
        # except:
        #     pass

        try:
            result_frame   = []
            result_frame_1 = []
            result_frame_2 = []
        except:
            pass


        # # フレーム動画をmp4でファイル保存
        # size=(640,480)#サイズ指定
        # frame_rate = int(4)#フレームレート
        # fourcc = cv2.VideoWriter_fourcc('m','p','4','v')#保存形式
        # save = cv2.VideoWriter('d_test.mp4',fourcc, frame_rate, size)
        # for i in range(len(frames)):
        #     save.write(frames[i])
        # save.release()
                
        # mimamoriに渡すファィルを保存
        # print('mimamoriに渡すファィルを保存')
        # cv2.imwrite('image.jpg',result_frame)
        # cv2.imshow("test-max", result_frame)
        # cv2.waitKey(0) 
        # time.sleep(10)
        # cv2.destroyAllWindows()
        # time.sleep(3)


if __name__ == '__main__':
    try:
        main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        print('key in stop')
    except ValueError as e:
        print(e)
