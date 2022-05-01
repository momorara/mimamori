#!/usr/bin/python
"""
###########################################################################

人感センサーの状態を確認する。 

#Filename      :HumanSensorxx.py - > mimamorixx.py
2022/03/13  start
2022/03/14  変化が無い時に1時間に一度信号を出す。
    02
2022/03/15  連続してon-offを繰り返すと信号量が増えるので
    03      指定時間内のoffは無視するようにしてみる(データの流量制限)
2022/03/19  startのLEDを点灯
2022/03/22  mqttがエラーになると落ちる-->エラー対応
            pub名称変更 Limit Instant
    04      config.ini対応、HumanSensorディレクトリとした
2022/04/04  
    05      mail実装
    06      LINE実装
2022/04/05  twitter実装
            ambient実装
2022/04/06  machinist実装
2022/04/07  swの動作を シャットダウンとテスト送信とした。
2022/04/09  swの動作を調整
2022/04/10  長時間動作させてセンサーがパクるのを防ぐため
            10分に一度センサーの電源を切り入りしてみる
2022/04/16  Machinist エラー処理
    11
2022/04/18  センサーの感知をワンショットではなく、累積時間でやってみる
    12
2022/04/20  l_print設定、mail等流量制限
2022/04/23  Ambient送信整理
2022/04/24  mqtt削除
    13
2022/04/25  センサーの短い動作をキャンセル 1秒以下は無視
2022/04/26  センサーの短い動作をキャンセル 3秒以下は無視、ambient45を送信 センサーがSR602の場合のみ
            この場合、累積時間を短めにすべきかも
            LEDフラッシュの活殺
    14      Mashinist不具合解消
2022/04/27  パナソニックのセンサー用に改造
2022/04/28  EKMC160111 , SR602 両対応とした configにてsensor_nameで指定
    21      
2022/04/29  SR602とEKMC、2種の基板でプログラム共用するため
    22      sensor-pin 9と22をorで運用
2022/05/01  リリースにあたって、mimamoriとした
    01      通知メッセージをconfigに記載 message


次にやること
・基板、回路図を作成

############################################################################
"""
import RPi.GPIO as GPIO
import time
import subprocess
import configparser
import datetime
import getpass

import sendMail
import sendLINE
import sendTwitter
import sendAmbient
import sendMachinist

# ユーザー名を取得
dt_now = datetime.datetime.now()
print(dt_now)
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/mimamori/' # cronで起動する際には絶対パスが必要
print(path)

# config,iniから値取得
# ---------------------------------------------------------------------
# configparserの宣言とiniファイルの読み込み
config_ini = configparser.ConfigParser()
config_ini.read(path + 'config.ini', encoding='utf-8')
# ---------------------------------------------------------------------
# mail、LINE、Twitterで送るメッセージ
message = config_ini.get('DEFAULT', 'message')
# LEDフラッシュ LEDの点滅を活殺します。
LED_flash_on_off = int(config_ini.get('DEFAULT', 'LED_flash_on_off')) 


# センサー種類 SR602 or EKMC160111
sensor_name   = config_ini.get('SENSOR', 'sensor')
# 累積on時間の閾値
on_Threshold  = int(config_ini.get('SENSOR', 'on_Threshold')) 
# off経過時間の閾値
off_Threshold = int(config_ini.get('SENSOR', 'off_Threshold')) 

# mail LINE twitterの流量制限は同じです。
Flow_rate_limit = int(config_ini.get('DEFAULT', 'Flow_rate_limit')) 
Flow_rate_limit = Flow_rate_limit*60 # 単位を分→秒にする

mail_flag      = int(config_ini.get('MAIL', 'mail_flag')) 
LINE_flag      = int(config_ini.get('LINE', 'LINE_flag')) 
twitter_flag   = int(config_ini.get('TWITTER', 'twitter_flag')) 
ambient_flag   = int(config_ini.get('AMBIENT', 'ambient_flag')) 
machinist_flag = int(config_ini.get('MACHINIST', 'machinist_flag')) 
# ---------------------------------------------------------------------

# センサーによりGPIOピン設定を行う
sensor1 = 22
sensor2 = 9
    
# SR602用電源    
pow  = 11
# SW
sw   = 6
# 表示用LED
LED1 = 27
LED2 = 17
# LEDフラッシュをしない場合
if LED_flash_on_off == 0:LED1,LED2 = 18,18
"""  点灯の意味
LED1   短い点滅:人を検知していない、点灯:mail,LINEを送信中
LED2   点灯:人を検知した、スイッチを押されて 1 or 4秒経過した  短い点滅:ambient送信中
LED1,2 交互点滅:人を検知して累積時間経過した後60秒
"""
twitter_count = 0  # 同一メッセージ回避用

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

#print message at the begining ---custom function
def print_message():
    print()
    print ('|********************************|')
    print ('|   人感センサーの状態を確認     |')
    print ('|********************************|\n')
    print ('Program is running...')
    print ('Please press Ctrl+C to end the program...')
    log_print()
    log_print('sensor=        ',sensor_name)
    log_print('on累積閾値      ',on_Threshold,'秒')
    log_print('リセット時間     ',off_Threshold,'秒')
    log_print('Flow_rate_limit',Flow_rate_limit,'秒')
    log_print('mail_flag      ',mail_flag)
    log_print('LINE_flag      ',LINE_flag) 
    log_print('twitter_flag   ',twitter_flag) 
    log_print('ambient_flag   ',ambient_flag)
    log_print('machinist_flag ',machinist_flag) 
    log_print()

#setup function for some setup---custom function
def setup():
    GPIO.setwarnings(False)
    #set the gpio modes to BCM numbering
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sensor1,GPIO.IN)
    GPIO.setup(sensor2,GPIO.IN)
    GPIO.setup(sw,GPIO.IN)
    # GPIO.setup(sw2,GPIO.IN)
    GPIO.setup(pow,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(LED1,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(LED2,GPIO.OUT,initial=GPIO.LOW)

#read SW_PI_1's level
def Read_sensor1():
    if GPIO.input(sensor1):return 'on'
    return 'off'
def Read_sensor2():
    if GPIO.input(sensor2):return 'on'
    return 'off'

def Read_sw():
    if GPIO.input(sw):return 'on'
    return 'off'

def LED_flash(on,off,n):
    for i in range(n):
        GPIO.output(LED1,GPIO.HIGH)
        time.sleep(on)
        GPIO.output(LED1,GPIO.LOW)
        time.sleep(off)

def LED_flash60():
    # web側での1分流量制限回避 その間LED点滅
    timer60_start = time.time()
    while timer60_start + 60 > time.time():
        GPIO.output(LED1,GPIO.HIGH)
        time.sleep(0.4)
        GPIO.output(LED1,GPIO.LOW)
        GPIO.output(LED2,GPIO.HIGH)
        time.sleep(0.4)
        GPIO.output(LED2,GPIO.LOW)
        sw_contlor()

def ambient(mesg):
    # print('ambient-1',mesg)
    if ambient_flag == 1:
        # 流量制限して送信
        try:
            # print('ambient-2',mesg)
            sendAmbient.ambient(mesg)
        except:
            time.sleep(2)
            try:    sendAmbient.ambient(mesg)
            except: return 'err'
    return 'ok'

def machinist(mesg):
    # print('machinist-1',mesg)
    if machinist_flag == 1:
        # 流量制限して送信
        try:
            # print('machinist-2',mesg)
            sendMachinist.send_metric(mesg)
        except:
            time.sleep(2)
            try:    sendMachinist.send_metric(mesg)
            except: return 'err'
    return 'ok'

def sensorPower_offon():
    # センサーエラーの回避のため10分おきに
    GPIO.output(pow,GPIO.LOW)  # センサーの電源を切る
    time.sleep(2)
    GPIO.output(pow,GPIO.HIGH) # センサーの電源を入れる
    time.sleep(10)
    log_print('センサーの電源を切り入り')

# スイッチの状態読み取り 押された時間により シャットダウンとテスト送信を行う
def sw_contlor():
    if Read_sw() == 'on' :# シャットダウン 
        sw_on = time.time()
        while Read_sw() == 'on':
            time.sleep(0.2)
            sw_off = time.time()
            sw_on_time = sw_off-sw_on
            if sw_on_time > 1 and sw_on_time < 1.4:
                print(sw_on_time)
                GPIO.output(LED2,GPIO.HIGH)
                time.sleep(0.4)
                GPIO.output(LED2,GPIO.LOW)
            if sw_on_time > 4 and sw_on_time < 4.4:
                print(sw_on_time)
                GPIO.output(LED2,GPIO.HIGH)
                time.sleep(0.4)
                GPIO.output(LED2,GPIO.LOW)
        print(sw_on_time)

        if sw_on_time > 4:
            log_print('シャットダウンシーケンス')
            GPIO.output(LED1,GPIO.HIGH)
            GPIO.output(LED2,GPIO.HIGH)
            time.sleep(2)
            GPIO.output(LED1,GPIO.LOW)
            GPIO.output(LED2,GPIO.LOW)
            subprocess.run('sudo shutdown now',shell=True)

        if sw_on_time > 1:
            log_print('test sensor on')
            LED_flash(0.2,0.2,5)
            GPIO.output(LED1,GPIO.HIGH)

            # swが1秒以上押されたので、全てのデータを送信します。
            ambient(75)
            machinist(75)
            send_message('見守りテスト-1')

            time.sleep(0.5)
            GPIO.output(LED1,GPIO.LOW)

def send_message(msg):
    if mail_flag == 1:# mailフラグ1の時だけ実行
        log_print('**********  mail send  ***********')
        sendMail.sendMail('みまもりメール',msg)
    if LINE_flag == 1:# LINEフラグ1の時だけ実行
        log_print('**********  LINE send  ***********')
        sendLINE.Line_sendMessage(msg)
    if twitter_flag == 1:# twitterフラグ1の時だけ実行
        log_print('********  twitter send   *********',twitter_count)
        mesg = msg + str(twitter_count)
        twitter_count += 1
        # twitterは同じ内容の投稿はキャンセルされるのでカウンターをつけました。
        sendTwitter.sendTwitter(mesg)

def send_signal(num,flag):
    # webシステムに数値を投げる flag:1なら61秒待つ
    machinist(num)
    # time.sleep(61)
    timer61s = time.time() + 61
    while (timer61s > time.time())  and flag == 1:
        GPIO.output(LED2,GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(LED2,GPIO.LOW)
        time.sleep(0.2)
        sw_contlor()
    ambient(num)

    # ambienは    先着優先・後着廃棄
    # machinistは 後着上書き
    # のようなので、61秒あければ、分単位で丸められないハズ

    # プログラム起動時 99
    # 人がいた 75
    # 累積で人がいた 100
    # リセット 25
    # 毎正時 20
    # ヘルスチェックのため送信 15 / 15,30,45分


def main():

    send_signal(95,0)

    # センサーの電源を入れる
    GPIO.output(pow,GPIO.HIGH)

    # EKMC160111は電源投入後30秒間不安定になるので、エージング
    if sensor_name == 'EKMC160111':
        timer30_start = time.time()
        while timer30_start + 30 > time.time():
            GPIO.output(LED1,GPIO.HIGH)
            time.sleep(0.4)
            GPIO.output(LED1,GPIO.LOW)
            GPIO.output(LED2,GPIO.HIGH)
            time.sleep(0.4)
            GPIO.output(LED2,GPIO.LOW)

    # タイムの初期値設定
    time_start = time.time()

    # スタートLEDフラッシュ
    LED_flash(0.2,0.1,5)

    one_time = 61                # 毎正時確認用
    one_time15 = 99              # 毎15分確認用
    Flow_rate_limit_end = 0      # mail流量制限用
    onTime_sum = 0               # on積算タイマー

    print_message()
    send_signal(99,0)
    while True:

        dt_now = datetime.datetime.now().strftime('%Y/%m/%dT%H:%M')
        if  Read_sensor1() == 'on' or Read_sensor2() == 'on': #-----------------------on動作-----------------------
            GPIO.output(LED2,GPIO.HIGH)
            onTimer = time.time()
            onStop = time.time()
            while Read_sensor1() == 'on' or Read_sensor2() == 'on':
                time.sleep(0.1)

            onTime = time.time() - onStop                 # onだった時間を記録
            if (sensor_name == 'SR602'):
                log_print(dt_now,'onTime ',int(onTime *10)/10)
            if (onTime < 2.1) and (sensor_name == 'SR602'): # onだった時間が3秒未満の場合はキャンセル  SR602のみ
                log_print('onTimeが短いのでキャンセル')
                onTime_sum = onTime_sum - onTime
                if onTime_sum < 0:onTime_sum = 0
                send_signal(45,0) # 仮の送信
            else:
                onTime_sum = onTime_sum + time.time() - onTimer # onだった時間を積算記録
                log_print(dt_now,'onTime_sum',int(onTime_sum *10)/10)
                # onで75
                send_signal(75,0)
            GPIO.output(LED2,GPIO.LOW)

        if onTime_sum > on_Threshold: #onの積算時間がon_sum_Thresholdを超えたら デフォ30s
            log_print('人がいた')
            LED_flash(0.2,0.2,5)
            onTimer     = 0
            onTime_sum = 0
            # LED_flash60()    # web側での1分流量制限回避
            send_signal(100,1) # 人が居たで100

            # mail 流量制限時限を超えれば送信する
            log_print('---mail---',int(Flow_rate_limit_end - time_start),int(time.time() - time_start))
            if Flow_rate_limit_end < time.time():
                # mail 流量制限時限を設定
                Flow_rate_limit_end = int(time.time() + Flow_rate_limit)
                send_message(message) # mail,LINE,Twitter送信


        if Read_sensor1() == 'off' and Read_sensor2() == 'off': #--------------------off動作--------------------------
            # send_signal(25,0)
            offTimer = time.time()
            while Read_sensor1() == 'off' and Read_sensor2() == 'off':
                GPIO.output(LED1,GPIO.HIGH)
                time.sleep(0.05)
                GPIO.output(LED1,GPIO.LOW)
                time.sleep(0.2)
                # offの間に色々やりましょう
                dt_now = datetime.datetime.now()

                # 毎正時に1度だけ10データを出す
                if (dt_now.minute == 0) :
                    if (one_time != dt_now.minute):
                        one_time = dt_now.minute
                        # ヘルスチェックのため中間値送信
                        send_signal(20,0)
                else:one_time = 61
                # 毎15,30,45に15データを出す
                if (dt_now.minute % 15  == 0) and (dt_now.minute / 15 > 0) :
                    if (one_time15 != dt_now.minute):
                        one_time15 = dt_now.minute
                        # SR602の場合に電源をoff-onする
                        if sensor_name == 'SR602':sensorPower_offon()
                        send_signal(15,0)
                else:one_time15 = 99

                # スイッチの状態読み取り シャットダウンとテスト送信を行う
                sw_contlor()

            if time.time() - offTimer > off_Threshold:# off状態が連続off_reset_Threshold秒経過 デフォ60s
                onTime_sum = 0 # on積算タイマーリセット
                log_print('リセット')
                send_signal(25,0)

 

#define a destroy function for clean up everything after the script finished
def destroy():
    # センサー電源切
    GPIO.output(pow,GPIO.LOW)
    #release resource
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    try:
        main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        destroy()
    except ValueError as e:
        log_print(e)
