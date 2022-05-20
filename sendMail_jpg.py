# -*- coding: utf-8 -*-

"""
2022/04/04  見守り対応
2022/05/08  jpgの送信対応
2022/05/09  jpgファイルが無い時対応
            to_addressの3通対応
            configにアドレスを追加するだけで良い   
"""

#################### メール送信 ###############################
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import datetime
import configparser
import getpass

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from os.path import basename


# ユーザー名を取得
user_name = getpass.getuser()
# print('user_name',user_name)
path = '/home/' + user_name + '/mimamori/' # cronで起動する際には絶対パスが必要


# config,iniから値取得
# --------------------------------------------------
# configparserの宣言とiniファイルの読み込み
config_ini = configparser.ConfigParser()
config_ini.read(path + 'config.ini', encoding='utf-8')
# --------------------------------------------------
host_s     = config_ini.get('MAIL', 'host_s')
username_s = config_ini.get('MAIL', 'username_s')
password_s = config_ini.get('MAIL', 'password_s')
send_add_1 = config_ini.get('MAIL', 'to_address')
try:
    send_add_2 = config_ini.get('MAIL', 'to_address_1')
    send_add_3 = config_ini.get('MAIL', 'to_address_2')
except:
    send_add_2 = 'no_send'
    send_add_3 = 'no_send'
# --------------------------------------------------
def sendMail(subject,body):
    sendMail_n(subject,body,    send_add_1)
    if send_add_2 != 'no_send':
        sendMail_n(subject,body,send_add_2)
    if send_add_3 != 'no_send':
        sendMail_n(subject,body,send_add_3)

def sendMail_n(subject,body,to_address):
    try:
        # 送信メール作成・送信
        dt_now = datetime.datetime.now()
        # time_stump = str(dt_now.month)  + "/" + str(dt_now.day) + " " +  str(dt_now.hour) + "時" + str(dt_now.minute) +  "分" 
        time_stump = str(dt_now.hour) + "時" + str(dt_now.minute) +  "分" 
        
        charset = 'iso-2022-jp'

        msg = MIMEMultipart()
        msg_subject = subject + " " + time_stump
        msg['Subject'] = Header(msg_subject.encode(charset), charset)
        msg["To"] = to_address
        smtp_obj = smtplib.SMTP(host_s, 587)
        smtp_obj.ehlo()
        smtp_obj.starttls()

        # 写真を添付
        jpg_path = 'image.jpg'
        with open(jpg_path, "rb") as f:
            photo = MIMEApplication(
                f.read(),
                Name=basename(jpg_path)
            )
        photo['Content-Disposition'] = 'attachment; filename="%s"' % basename(jpg_path)
        msg.attach(photo)
        smtp_obj.login(username_s, password_s)
        smtp_obj.sendmail(username_s, to_address, msg.as_string())
        smtp_obj.quit()

        print('mail send')
    except :
        print("mail send error")
        pass

def main():
    # sendmail = 'pc_mailbox@mineo.jp'
    sendMail('見守り状況に変化がありました。test ','test')

if __name__ == '__main__':
    # try:
        main()
        #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    # except :
    #     print("mail error")
    # else:
    #     print('例外は発生しませんでした。')
    # finally:
    #     print('実行が終了しました')