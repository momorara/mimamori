#!/usr/bin/python
"""
###########################################################################

人感センサーの状態を確認する。 

#Filename      :HumanSensorxx.py

一つのGPIOピンを確認する

############################################################################
"""
import RPi.GPIO as GPIO
import time
import datetime
# import subprocess
# import configparser
# import datetime
# import getpass

# import pub_HumanSensor_Limit
# import pub_HumanSensor_Instant
# import sendMail
# import sendLINE
# import sendTwitter
# import sendAmbient
# import sendMachinist

# # ユーザー名を取得
# dt_now = datetime.datetime.now()
# print(dt_now)
# user_name = getpass.getuser()
# print('user_name',user_name)
# path = '/home/' + user_name + '/HumanSensor/' # cronで起動する際には絶対パスが必要
# print(path)

# # config,iniから値取得
# # --------------------------------------------------
# # configparserの宣言とiniファイルの読み込み
# config_ini = configparser.ConfigParser()
# config_ini.read(path + 'config.ini', encoding='utf-8')
# # --------------------------------------------------
# mqtt_flag       = int(config_ini.get('MQTT', 'mqtt_flag')) 
# instant_flag    = int(config_ini.get('MQTT', 'instant_flag'))    # 瞬時送信の有無
# mqtt_flow_rate_limit = int(config_ini.get('MQTT', 'mqtt_flow_rate_limit')) # データの流量制限n秒間は流量制限する
# mqtt_flow_rate_limit = mqtt_flow_rate_limit*60 # 単位を分→秒にする
# print(instant_flag,mqtt_flow_rate_limit)

# # mail LINE twitterの流量制限は同じです。
# Flow_rate_limit = int(config_ini.get('DEFAULT', 'Flow_rate_limit')) 
# Flow_rate_limit = Flow_rate_limit*60 # 単位を分→秒にする

# mail_flag    = int(config_ini.get('MAIL', 'mail_flag')) 
# LINE_flag    = int(config_ini.get('LINE', 'LINE_flag')) 
# twitter_flag = int(config_ini.get('TWITTER', 'twitter_flag')) 
# ambient_flag = int(config_ini.get('AMBIENT', 'ambient_flag')) 
# machinist_flag = int(config_ini.get('MACHINIST', 'machinist_flag')) 
  
# # SW
sw1    = 6
# # set GPIO 0 as sensor pin
sensor = 9
pow    = 11
# # 表示用LED
LED1   = 27
LED2   = 17

# ###################log print#####################
# # 自身のプログラム名からログファイル名を作る
# import sys
# args = sys.argv
# logFileName = args[0].strip(".py") + "_log.csv"
# print(logFileName)
# # ログファイルにプログラム起動時間を記録
# import csv
# # 日本語文字化けするので、Shift_jisやめてみた。
# f = open(logFileName, 'a')
# csvWriter = csv.writer(f)
# csvWriter.writerow([datetime.datetime.now(),'  program start!!'])
# f.close()
# #----------------------------------------------
# def log_print(msg1="",msg2="",msg3=""):
#     # エラーメッセージなどをプリントする際に、ログファイルも作る
#     # ３つまでのデータに対応
#     print(msg1,msg2,msg3)
#     # f = open(logFileName, 'a',encoding="Shift_jis") 
#     # 日本語文字化けするので、Shift_jisやめてみた。
#     f = open(logFileName, 'a')
#     csvWriter = csv.writer(f)
#     csvWriter.writerow([datetime.datetime.now(),msg1,msg2,msg3])
#     f.close()
# ################################################

# #print message at the begining ---custom function
# def print_message():
#     print ('|********************************|')
#     print ('|   人感センサーの状態を確認          |')
#     print ('|********************************|\n')
#     print ('Program is running...')
#     print ('Please press Ctrl+C to end the program...')

# #setup function for some setup---custom function
def setup():
    GPIO.setwarnings(False)
    #set the gpio modes to BCM numbering
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sensor,GPIO.IN)
    GPIO.setup(sw1,GPIO.IN)
    # GPIO.setup(sw2,GPIO.IN)
    GPIO.setup(pow,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(LED1,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(LED2,GPIO.OUT,initial=GPIO.LOW)

#read SW_PI_1's level
def Read_sensor():
    if (GPIO.input(sensor)):
        sw_ = 'on'
    else:
        sw_ = 'off'
    return sw_

# def Readsw1():
#     if (GPIO.input(sw1)):
#         sw_ = 'on'
#     else:
#         sw_ = 'off'
#     return sw_

# def LED_flash(on,off,n):
#     for i in range(n):
#         GPIO.output(LED1,GPIO.HIGH)
#         time.sleep(on)
#         GPIO.output(LED1,GPIO.LOW)
#         time.sleep(off)

# def mqtt_Limit(mesg):
#     if mqtt_flag == 1:
#         # 流量制限して送信
#         try:
#             pub_HumanSensor_Limit.mqtt_pub(mesg)
#         except:
#             time.sleep(1)
#             try:
#                 pub_HumanSensor_Limit.mqtt_pub(mesg)
#             except:
#                 return 'err'
#     return 'ok'

# def mqtt_Instant(mesg):
#     if instant_flag == 1 and mqtt_flag == 1:
#         # 瞬時に送信
#         try:
#             pub_HumanSensor_Instant.mqtt_pub(mesg)
#         except:
#             time.sleep(1)
#             try:
#                 pub_HumanSensor_Instant.mqtt_pub(mesg)
#             except:
#                 return 'err'
#     return 'ok'

# def ambient_Limit(mesg):
#     # print('ambient-1',mesg)
#     if ambient_flag == 1:
#         # 流量制限して送信
#         try:
#             # print('ambient-2',mesg)
#             sendAmbient.ambient(mesg)
#         except:
#             time.sleep(1)
#             try:
#                 sendAmbient.ambient(mesg)
#             except:
#                 return 'err'
#     return 'ok'

# def machinist(mesg):
#     # print('machinist-1',mesg)
#     if machinist_flag == 1:
#         # 流量制限して送信
#         try:
#             # print('machinist-2',mesg)
#             sendMachinist.send_metric(mesg)
#         except:
#             time.sleep(1)
#             try:
#                 sendMachinist.send_metric(mesg)
#             except:
#                 return 'err'
#     return 'ok'

#main function
def main():
    # # センサーの電源を入れる
    GPIO.output(pow,GPIO.HIGH)
    # #
    # LED_flash(0.2,0.1,5)

    # HumanSensor = 'off'          # 現在状態取得
    # last_time = 'fast time'      # 状態変化確認用
    one_time = 61                # 毎正時確認用
    one_time10 = 99              # 毎10分確認用
    # mqtt_flow_rate_limit_end = 0 # mqtt流量制限用
    # Flow_rate_limit_end = 0      # mail流量制限用

    # # off方向のリミット　固定1分
    # off_limit = 61
    # # 同一メッセージ回避用
    # twitter_count = 0



    # print_message()
    while True:
        HumanSensor = Read_sensor()
        print(HumanSensor,' ',end='', flush=True)
        if HumanSensor == 'on':
            GPIO.output(LED1,GPIO.HIGH)
        else:
            GPIO.output(LED1,GPIO.LOW)
        time.sleep(1)


        # if HumanSensor =='off':
        #     log_print('off',last_time)
            
        #     # mqtt
        #     if last_time != HumanSensor: # 状態変化があった場合
        #         last_time = HumanSensor
        #         err_Instant = mqtt_Instant('22')

        #         # off方向の送信を1分に1回に制限する。
        #         if off_limit != datetime.datetime.now().minute:
        #             mqtt_Limit('25')
        #             ambient_Limit(25)
        #             machinist(25)
        #             off_limit = datetime.datetime.now().minute

        #         if err_Instant == 'err':
        #             log_print('mqtt err')

        # else:
        #     log_print('on',last_time)
            
        #     GPIO.output(LED1,GPIO.HIGH)
        #     if last_time != HumanSensor: # 状態変化があった場合
        #         last_time = HumanSensor

        #         log_print('---mqtt---',mqtt_flow_rate_limit_end-1648610304,int(time.time()-1648610304))
        #         # mqtt 流量制限時限を超えれば送信する
        #         if mqtt_flow_rate_limit_end < time.time():
        #             # mqtt 流量制限時限を設定
        #             mqtt_flow_rate_limit_end = int(time.time() + mqtt_flow_rate_limit)
        #             mqtt_Limit('75')
        #             ambient_Limit(75)
        #             machinist(75)
                    
        #         mqtt_Instant('77')
                
        #         GPIO.output(LED2,GPIO.HIGH)

        #         # mail 流量制限時限を超えれば送信する
        #         log_print('---mail---',Flow_rate_limit_end-1648610304,int(time.time()-1648610304))
        #         if Flow_rate_limit_end < time.time():
        #             # mail 流量制限時限を設定
        #             Flow_rate_limit_end = int(time.time() + Flow_rate_limit)
        #             # mail 
        #             if mail_flag == 1:# mailフラグ1の時だけ実行
        #                 log_print('**********  mail send  ***********')
        #                 sendMail.sendMail('みまもりメール','見守り状況に変化がありました')

        #             if LINE_flag == 1:# LINEフラグ1の時だけ実行
        #                 log_print('**********  LINE send  ***********')
        #                 sendLINE.Line_sendMessage('見守り状況に変化がありました。')

        #             if twitter_flag == 1:# twitterフラグ1の時だけ実行
        #                 log_print('********  twitter send   *********',twitter_count)
        #                 mesg = '見守り状況に変化がありました。' + str(twitter_count)
        #                 twitter_count += 1
        #                 # twitterは同じ内容の投稿はキャンセルされるのでカウンターをつけました。
        #                 sendTwitter.sendTwitter(mesg)

        #         time.sleep(1)
        #     time.sleep(0.1)
        #     GPIO.output(LED1,GPIO.LOW)
        
        # time.sleep(2)
        # GPIO.output(LED2,GPIO.LOW)

        # # 毎正時に1度だけ0データを出し、直ぐに元の状態データを出す。
        # # 毎正時確認
        # dt_now = datetime.datetime.now()
        # if (dt_now.minute == 0) :
        #     # 一度だけ確認
        #     if  (one_time != dt_now.minute) :
        #         one_time = dt_now.minute
        #         # ヘルスチェックのため中間値送信
        #         mqtt_Limit('0')
        #         mqtt_Instant('0')
        #         ambient_Limit(10)
        #         machinist(10)
        #         # 元状態送信
        #         if HumanSensor =='off':
        #             err_Limit   = mqtt_Limit('25')
        #             err_Instant = mqtt_Instant('22')
        #             ambient_Limit(25)
        #             machinist(25)
        #         else:
        #             err_Limit   = mqtt_Limit('75')
        #             err_Instant = mqtt_Instant('77')
        #             ambient_Limit(75)
        #             machinist(75)
        #         if err_Limit == 'err' or err_Instant == 'err' :
        #             log_print('mqtt err')
        # else:
        #     one_time = 61

        # # 毎10分確認 センサーの電源を切って入れる
        # dt_now = datetime.datetime.now()
        # if (dt_now.minute % 1  == 0) :
        #     # 一度だけ確認
        #     if  (one_time10 != dt_now.minute) :
        #         one_time10 = dt_now.minute
        #         # センサーの電源を切って入れる
        #         GPIO.output(pow,GPIO.LOW)
        #         time.sleep(2)
        #         GPIO.output(pow,GPIO.HIGH)
        #         time.sleep(10)
        #         print('センサーの電源を切り入り')

        # # スイッチの状態読み取り
        # sw1_ = Readsw1()
        # if sw1_ == 'on' :# シャットダウン 
        #     sw_on = time.time()
        #     while Readsw1() == 'on':
        #         time.sleep(0.2)
        #         sw_off = time.time()
        #         sw_on_time = sw_off-sw_on
        #         if sw_on_time > 1 and sw_on_time < 1.4:
        #             log_print(sw_on_time)
        #             GPIO.output(LED2,GPIO.HIGH)
        #             time.sleep(0.4)
        #             GPIO.output(LED2,GPIO.LOW)
        #         if sw_on_time > 4 and sw_on_time < 4.4:
        #             log_print(sw_on_time)
        #             GPIO.output(LED2,GPIO.HIGH)
        #             time.sleep(0.4)
        #             GPIO.output(LED2,GPIO.LOW)
        #     log_print(sw_on_time)

        #     if sw_on_time > 4:
        #         log_print('シャットダウンシーケンス')
        #         GPIO.output(LED1,GPIO.HIGH)
        #         GPIO.output(LED2,GPIO.HIGH)
        #         time.sleep(2)
        #         GPIO.output(LED1,GPIO.LOW)
        #         GPIO.output(LED2,GPIO.LOW)
        #         subprocess.run('sudo shutdown now',shell=True)

        #     if sw_on_time > 1:
        #         log_print('test sensor on')
        #         LED_flash(0.2,0.2,5)
        #         GPIO.output(LED1,GPIO.HIGH)

        #         # swが1秒以上押されたので、全てのデータを送信します。
        #         mqtt_Limit('75')
        #         ambient_Limit(75)
        #         machinist(75)

        #         # mail 
        #         if mail_flag == 1:# mailフラグ1の時だけ実行
        #             log_print('**********  mail send  ***********')
        #             sendMail.sendMail('みまもりテストメール','見守りテスト')

        #         if LINE_flag == 1:# LINEフラグ1の時だけ実行
        #             log_print('**********  LINE send  ***********')
        #             sendLINE.Line_sendMessage('みまもりテストメール')

        #         if twitter_flag == 1:# twitterフラグ1の時だけ実行
        #             log_print('********  twitter send   *********',twitter_count)
        #             mesg = 'みまもりテストメール' + str(twitter_count)
        #             twitter_count += 1
        #             # twitterは同じ内容の投稿はキャンセルされるのでカウンターをつけました。
        #             sendTwitter.sendTwitter(mesg)

        #         sw_on_time = 0
        #         time.sleep(2)
        #         GPIO.output(LED1,GPIO.LOW)

#define a destroy function for clean up everything after the script finished
def destroy():
    # センサー電源切
    GPIO.output(pow,GPIO.LOW)
    #release resource
    GPIO.cleanup()
#
# if run this script directly ,do:
if __name__ == '__main__':
    setup()
    try:
        main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        destroy()
    except ValueError as e:
        # log_print(e)
        pass