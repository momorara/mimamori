#!/bin/env python3

"""
LINE01.py

LINEにトークンを使ってメッセージを送ります。

2022/04/04  見守り対応
2022/05/08  jpgの送信対応
2022/05/09  jpgファイルが無い時対応
"""
import requests
import configparser
import getpass
import os

# ユーザー名を取得
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/mimamori/' # cronで起動する際には絶対パスが必要


# config,iniから値取得
# --------------------------------------------------
# configparserの宣言とiniファイルの読み込み
config_ini = configparser.ConfigParser()
config_ini.read(path + 'config.ini', encoding='utf-8')
# --------------------------------------------------
token_kakunin     = config_ini.get('LINE', 'token_kakunin')
# --------------------------------------------------

def Line_sendMessage(msg):
    try:
        jpg_filename = 'image.jpg'

        token = token_kakunin     
        payload = {'message': msg}  # 送信メッセージ
        url     = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': 'Bearer ' + token}
        payload = {"message" :  msg}

        if os.path.exists(jpg_filename):
            #jpgを指定
            files = {"imageFile":open(jpg_filename,'rb')}
            #rbはバイナリファイルを読み込む
            res = requests.post(url ,headers = headers ,params=payload,files=files)
            print(res)
        else:
            # jpgファイルが無い場合
            payload = {'message': '見守り状況に変化がありました。'+'\n'+'image.jpgがみつかりません。'} 
            res = requests.post(url, data=payload, headers=headers)    # LINE NotifyへPOST

    except:
        print('Line send error')
        pass

def main():
    Line_sendMessage('見守り状況に変化がありました。test')


if __name__ == '__main__':
    # try:
        main()
        #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    # except KeyboardInterrupt:
    #     #destroy()
    #     pass
    # except :
    #     #エラー処理
    #     print("エラー　通信エラーが考えられるので、しばらくして再開" )
    #     time.sleep(360) #6分休憩
    #     print('再開します。')
    #     print()
    #     try:
    #         # 一回再チャレンジ
    #         main()
    #         # 今度エラーが起こると直ぐ止まる。
    #     except :
    #         #エラー処理
    #         print("エラー　再開したが、再度エラーの模様　プログラム終了する。" )
    #         print()