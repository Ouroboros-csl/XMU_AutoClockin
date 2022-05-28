# 厦门大学疫情打卡爬虫
## 介绍
本项目基于python与selenium库提供厦门大学疫情自动打卡程序

## 要求 
- python == 3.9.7

## 使用

1. 首先创建conda虚拟环境
```
conda activate
conda create -n "your_env_name" python==3.9.7
```
2. 切换到conda虚拟环境，运行安装依赖库
```
conda activate "your_env_name"
pip install requirements.txt -r
```
3. 修改bat批处理文件,修改conda env路径

3. 打开qq邮箱smtp服务

4. 编写config.json文件
```
{
    "username" : "你的学号", 
    "password" : "你的密码", 
    "receiver" : "你的接收提醒邮件的邮箱号", 
    "host_server" : "smtp.qq.com",  
    "sender_qq" : "你的qq号",  
    "pwd" : "smtp的密钥",  
    "sender_qq_mail" : "你的qq邮箱"
}
```
5. 点击批处理文件即可自动运行