# machinist.py
import configparser
import json
import requests
import time
import getpass
import datetime

# ユーザー名を取得
user_name = getpass.getuser()
# print('user_name',user_name)
path = '/home/' + user_name + '/mimamori/' # cronで起動する際には絶対パスが必要

'''
Usage: metrics([config file])
メトリックをIIJのmachinistサービスに送る｡
config_fileは､省略時には｢.config｣を参照する｡
'''
URL = "https://gw.machinist.iij.jp/endpoint"


# config,iniから値取得
# --------------------------------------------------
# configparserの宣言とiniファイルの読み込み
config_ini = configparser.ConfigParser()
config_ini.read(path + 'config.ini', encoding='utf-8')
# --------------------------------------------------
agent       = config_ini["MACHINIST"]["agent"]
namespace   = config_ini["MACHINIST"]["namespace"]
metric_name = config_ini["MACHINIST"]["metric_name"]
key         = config_ini["MACHINIST"]["key"]
# --------------------------------------------------

# print(URL)
# print(agent)
# print(namespace)
# print(metric_name)
# print(key)

def send_metric(data):
  '''
  メトリックをサーバに送信する
  '''
  headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
  body = {
      "agent": agent,
      "metrics": [
          {
              "name"      : metric_name,
              "namespace" : namespace,
              "data_point": {
                    "value"   : data
              }
          }
      ]
  }
  dt_now = datetime.datetime.now().strftime('%dT%H:%M')
  print('machinist',data,dt_now)
  result = requests.post(URL, data=json.dumps(body), headers=headers)
  return result



if __name__ == "__main__":

  print('1')
  rc = send_metric(70)
  print('2')
  time.sleep(61)
  rc = send_metric(25)
  time.sleep(61)
  rc = send_metric(70)
  time.sleep(61)
  rc =  send_metric(25)
  time.sleep(61)
  if rc.status_code == 200:
    print("OK")
  else:
    print(f"NG: Return code {rc.status_code}")