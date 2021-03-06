"""

2022/04/04  見守り対応
2022/05/09  to_addressの3通対応
            configにアドレスを追加するだけで良い    
"""

####################　メール送信　###############################
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import datetime
import configparser
import getpass

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
        msg = MIMEText(body, 'plain', charset)
        msg_subject = subject + " " + time_stump
        msg['Subject'] = Header(msg_subject.encode(charset), charset)
        msg["To"] = to_address
        smtp_obj = smtplib.SMTP(host_s, 587)
        smtp_obj.ehlo()
        smtp_obj.starttls()
        smtp_obj.login(username_s, password_s)
        smtp_obj.sendmail(username_s, to_address, msg.as_string())
        smtp_obj.quit()

        print('mail send ',to_address)
    except :
        print("mail send error")
        pass

def main():
    sendmail = 'pc_mailbox@mineo.jp'
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