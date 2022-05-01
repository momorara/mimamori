#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ambientライブラリのインストール
$ pip3 install git+https://github.com/AmbientDataInc/ambient-python-lib.git
$ pip3 list | grep ambient
ambient 0.1.9  

2022/03/26  Ambient対応
2022/04/05  見守り対応
"""
import configparser
import getpass

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
ch        =  int(config_ini.get('AMBIENT', 'ch'))
write_key =      config_ini.get('AMBIENT', 'write_key')
# --------------------------------------------------


# =================================================
#           ライブラリインポート
import ambient
import requests
import time
import datetime

# Ambient対応 
"""                チャネルID       ライトキー        """
# am = ambient.Ambient(49320, "c678e31abbcb4649")
am = ambient.Ambient(ch, write_key)
""""""""""""""""""""""""""""""""""""""""""""""""""""""

def ambient(data):
    dt_now = datetime.datetime.now().strftime('%dT%H:%M')
    print('ambient',data,dt_now,' ',end='', flush=True)
    try:
        res = am.send({"d1": data})
    except requests.exceptions.RequestException as e:
        print('request failed: ', e)

def main():
    ambient(10)
    time.sleep(4)
    ambient(90)
    time.sleep(4)
    ambient(10)
    time.sleep(4)
    ambient(90)


if __name__ == '__main__':
    try:
        main()
        #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        #destroy()
        pass