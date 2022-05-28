from argparse import Action
import time
import numpy as np
import selenium
from os.path import join as pjoin
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import warnings
import pickle as pkl
import pymysql
from datetime import datetime
import json
import pytz

class Health_clock_in():
    def __init__(self):
        with open("config.json") as f :self.kwargs = json.load(f)
    
    def check_time(self,t):
        if (t.hour>=18)|(t.hour<=8):
            print(f"Check time: {t.strftime('%Y-%m-%d %H:%M:%S %Z%z')},不在打卡时间内 ")
            return False
        else:
            print(f"Check time: {t.strftime('%Y-%m-%d %H:%M:%S %Z%z')},打卡时间内 ")
            return True


    def get_zone_time(self, return_time = False):
        time_zone = pytz.timezone('Asia/Shanghai')
        t = datetime.fromtimestamp(int(time.time()),time_zone)
        if return_time:
            return t
        else: 
            return t.strftime('%Y-%m-%d %H:%M:%S %Z%z')

    def clock_in(self):
        # 开启Chrome驱动，进入入口网站
        webdriver = Chrome()
        webdriver.get("https://xmuxg.xmu.edu.cn/platform")
        time.sleep(10)
        webdriver.maximize_window()
        
        # 选择统一身份认证
        verify_button = webdriver.find_element(by = By.XPATH, value = "/html/body/div[1]/div/div[3]/div[2]/div/button[3]")
        ActionChains(webdriver).click(verify_button).perform()
        time.sleep(10)
        
        #打印认证网站网址
        print(f"page change,current url:{webdriver.current_url}")
        page1 = webdriver.window_handles[-1]
        webdriver.switch_to.window(page1)
        time.sleep(10)

        # 登录输入用户名/密码
        webdriver.find_element(by = By.XPATH, 
                            value = "/html/body/div[3]/div[2]/div[2]/div/div[3]/div/form/p[1]/input").send_keys(self.kwargs.get("username"))
        time.sleep(1)
        webdriver.find_element(by = By.XPATH, 
                            value = "/html/body/div[3]/div[2]/div[2]/div/div[3]/div/form/p[2]/input").send_keys(self.kwargs.get("password"))
        time.sleep(1)
        print(f"Login action: username:%s, password:%s" % (self.kwargs.get("username"), self.kwargs.get("password")))
        login_button = webdriver.find_element(by = By.XPATH, 
                            value = "/html/body/div[3]/div[2]/div[2]/div/div[3]/div/form/p[4]/button")
        ActionChains(webdriver).click(login_button).perform()
        time.sleep(5)
        
        # 进入信息网站，选择疫情打卡模块
        page2 = webdriver.window_handles[-1]
        webdriver.switch_to.window(page2)
        print(f"page change, current url:{webdriver.current_url}")
        
        health_button = webdriver.find_element(by = By.XPATH, 
                        value = "/html/body/div[1]/div/div/div/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]")
        ActionChains(webdriver).click(health_button).perform()
        time.sleep(5)
        
        # 进入疫情打卡页面
        page3 = webdriver.window_handles[-1]
        webdriver.switch_to.window(page3)
        print(f"page change, current url:{webdriver.current_url}")
        # 选择表单界面
        table_button = webdriver.find_element(by = By.XPATH, 
                        value = "/html/body/div[1]/div/div/div/div/div[1]/div[2]/div/div[3]/div[2]")
        ActionChains(webdriver).click(table_button).perform()
        time.sleep(5)
        
        # 拉到底线日期处，选择选项
        bottom_line = webdriver.find_element(by = By.XPATH, 
                        value = "/html/body/div[1]/div/div/div/div/div[2]/div[1]/div/div/div/div[4]/div/div[41]/div/div/div/span[1]")
        webdriver.execute_script("arguments[0].scrollIntoView()", bottom_line)
        
        # 检查是否已经打卡
        check_frame = webdriver.find_element(by = By.XPATH, 
                        value = '//*[@id="select_1582538939790"]/div/div/span[1]')
        check_text = check_frame.text
        if check_text == "是 Yes":
            dt_str = self.get_zone_time()
            print(f"Check time: {dt_str}, 已打卡！")
        else:
            webdriver.find_element(by = By.XPATH, 
                            value = '//*[@id="select_1582538939790"]/div/div').click()
            time.sleep(2)
            webdriver.find_element(by = By.XPATH, 
                            value = "/html/body/div[8]/ul/div/div[3]/li").click()
            time.sleep(2)
            # 保存打卡内容
            save_button = webdriver.find_element(by = By.XPATH, 
                            value = "/html/body/div[1]/div/div/div/div/div[2]/div[1]/div/div/div/span/span")
            try:
                save_button.click()
                time.sleep(1)
                webdriver.switch_to.alert.accept()
                time.sleep(4)
                intext = f"Check time: {self.get_zone_time()} ,今日成功打卡! "
                intitle = "Clockin Seccessfully runs"
                self.SendMail(intitle, intext)
                
            except:
                save_button.click()
                message = webdriver.find_element(by = By.XPATH, value = "/html/body/div[8]/div/pre")
                msg_text = message.text
                intext = f"ERROR, alert message:{msg_text} "
                intitle = "Clockin error"
                self.SendMail(intitle, intext)
                time.sleep(5)

    def run_clock_in(self):
        while True:
            t = self.get_zone_time(return_time = True)
            if self.check_time(t):
                self.clock_in()

            time.sleep(2*60*60 - 60)
    
   
    @staticmethod
    def SendMail(intitle, intext):
        
        def get_world_time_now(strftime="%H:%M",timezone='Asia/Shanghai'):
            return datetime.fromtimestamp(int(time.time()),pytz.timezone(timezone)).strftime(strftime)
        
        from email.mime.text import MIMEText
        from email.header import Header
        from smtplib import SMTP_SSL
        
        with open('config.json','rb') as f: config = json.load(f)
        
        host_server = config['host_server']  # QQ邮箱smtp服务器
        sender_qq = config['sender_qq']  # 发送者QQ
        pwd = config['pwd']  # 密码，通常为授权码
        sender_qq_mail = config['sender_qq_mail']  # 发送者QQ邮箱地址
        username = config['username']
        receiver = config['receiver']

        mail_content = intext + str(get_world_time_now(strftime="%Y-%m-%d %H:%M:%S %Z%z"))
        mail_content += '1> Username:' + username + '\n'
        mail_content += '2> Time:' + str(get_world_time_now(strftime="%Y-%m-%d %H:%M:%S %Z%z")) + '\n'
        mail_content += '3> Your Email:' + receiver + '\n'
        mail_content += '4> Host Email:' + sender_qq + '\n'
        mail_title = intitle

        smtp = SMTP_SSL(host_server)
        smtp.set_debuglevel(1)
        smtp.ehlo(host_server)
        smtp.login(sender_qq, pwd)

        msg = MIMEText(mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_qq_mail
        msg["To"] = receiver
        smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
        smtp.quit()        
        
    def start_auto_clock_in(self):
        pass
        

if __name__ == "__main__":
    health_clock_in = Health_clock_in()
    health_clock_in.run_clock_in()

