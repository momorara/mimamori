#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Requests-OAuthlibのインストールはGitHubに記載の通り、
pip3 install requests requests_oauthlib

2019/11/12
Lib_twitter.py

2022/04/05  見守り対応
            twitterは同じ内容の投稿はキャンセルされる

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
CK     = config_ini.get('TWITTER', 'CK')
CS     = config_ini.get('TWITTER', 'CS')
AT     = config_ini.get('TWITTER', 'AT')
AS     = config_ini.get('TWITTER', 'AS')
# --------------------------------------------------

from requests_oauthlib import OAuth1Session

# ツイート投稿用のURL
url = "https://api.twitter.com/1.1/statuses/update.json"

# ツイート本文
# params = {"status": "Hello, World!"}

def sendTwitter(msg):
    try:
        # OAuth認証で POST method で投稿
        twitter = OAuth1Session(CK, CS, AT, AS)
        params = {"status": msg}
        req = twitter.post(url, params = params)
    except :
        print('twitter sen error')
        pass

def main():
    sendTwitter('見守り状況に変化がありました。test')


if __name__ == '__main__':
    try:
        main()
        #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        #destroy()
        pass