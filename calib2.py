# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 19:40:33 2018

@author: youle
"""

# coding:utf-8
import os
import time
import datetime
import socket

#初始化设备-宏定义
phase_enable = ['1','0','0','0']
flag = 0

#部分函数定义
def error_dct(rec,comm):
    if rec != comm: 
        print('机械臂返回错误，请检查后重试')
        exit()


#初始化设备-挂载设备
print(datetime.datetime.now())
time.sleep(0.1)
n = ''
while (n!="remount succeeded\n") :
    f = os.popen(r"adb remount", "r")
    time.sleep(1)
    n = f.read()
    f.close()
print("眼镜设备挂载成功")


#初始化设备-读取设备号
print(datetime.datetime.now())
f = os.popen(r"adb devices", "r")
shuchu = f.read()
f.close()
#print(shuchu)  
s = shuchu.split("\n")   # 切割换行
#print(s)
new = [x for x in s if x != '']  # 去掉空''
#print(new)
devices = []  # 可能有多个手机设备，获取设备名称
for i in new:
    dev = i.split('\tdevice')
    if len(dev)>=2:
        devices.append(dev[0])
if not devices:
    print("眼镜设备没连上,请连接手机重新执行")
    exit()
else:
    print("当前手机设备:%s"%str(devices))

 

#获取标定数据-初始化socket套接字
sk = socket.socket()
sk.bind(("192.168.0.1",7080))
sk.listen(5)
conn,address = sk.accept()
ret = str(conn.recv(1024),encoding="utf-8")
print("接收到设备数据"+ret)
time.sleep(0.1)
conn.sendall(bytes("cstwo",encoding="utf-8"))
print("已发送锁存校验数据")
time.sleep(0.1)
ret = str(conn.recv(1024),encoding="utf-8")
print(ret)
print("Socket通讯建立")


if phase_enable[0]=='1':
    #获取标定数据-P1S1S-IMU标定步骤1
    conn.sendall(bytes("P1S1S",encoding="utf-8"))
    print("已发送下一点位置数据")
    time.sleep(0.1)
    ret = str(conn.recv(1024),encoding="utf-8")
    print(ret)
    print("已移动到机械臂IMU标定1号点，开始1位置标定")
    time.sleep(14)
    f = os.popen(r"adb shell testimucal 1", "r")
    shuchu = f.read()
    f.close()
    n=2
    while(shuchu!='0'):
        print('标定失败，进行第['+str(n)+']次尝试')
        f = os.popen(r"adb shell testimucal 1", "r")
        shuchu = f.read()
        f.close()
        n=n+1
        if n>6:
            print('6次标定都失败，请注意是不是夜深人静，再进行重试')
            conn.sendall(bytes("GHOME",encoding="utf-8"))
            print("准备移动到装配点")
            time.sleep(1)
            ret = str(conn.recv(1024),encoding="utf-8")
            print(ret)
            error_dct(ret,'HOMED')
            conn.close()
            exit()
    print("IMU标定1结果"+shuchu)
    conn.sendall(bytes("P1S2S",encoding="utf-8"))
    print("准备移动到下一个点")
    
    
    #获取标定数据-P1S2S-IMU标定步骤2
    ret = str(conn.recv(1024),encoding="utf-8")
    print(ret)
    print("已移动到机械臂IMU标定2号点，开始2位置标定")
    time.sleep(14)
    f = os.popen(r"adb shell testimucal 2", "r")
    shuchu = f.read()
    f.close()
    n=2
    while(shuchu!='0'):
        print('标定失败，进行第['+str(n)+']次尝试')
        f = os.popen(r"adb shell testimucal 2", "r")
        shuchu = f.read()
        f.close()
        n=n+1
        if n>6:
            print('6次标定都失败，请注意是不是夜深人静，再进行重试')
            conn.sendall(bytes("GHOME",encoding="utf-8"))
            print("准备移动到装配点")
            time.sleep(1)
            ret = str(conn.recv(1024),encoding="utf-8")
            print(ret)
            error_dct(ret,'HOMED')
            conn.close()
            exit()
    print("IMU标定2结果"+shuchu)
    conn.sendall(bytes("P1S3S",encoding="utf-8"))
    print("准备移动到下一个点")
    
    
    #获取标定数据-P1S3S-IMU标定步骤3
    ret = str(conn.recv(1024),encoding="utf-8")
    print(ret)
    print("已移动到机械臂IMU标定3号点，开始3位置标定")
    time.sleep(14)
    f = os.popen(r"adb shell testimucal 3", "r")
    shuchu = f.read()
    f.close()
    n=2
    while(shuchu!='0'):
        print('标定失败，进行第['+str(n)+']次尝试')
        f = os.popen(r"adb shell testimucal 3", "r")
        shuchu = f.read()
        f.close()
        n=n+1
        if n>6:
            print('6次标定都失败，请注意是不是夜深人静，再进行重试')
            conn.sendall(bytes("GHOME",encoding="utf-8"))
            print("准备移动到装配点")
            time.sleep(1)
            ret = str(conn.recv(1024),encoding="utf-8")
            print(ret)
            error_dct(ret,'HOMED')
            conn.close()
            exit()
    print("IMU标定3结果"+shuchu)
    conn.sendall(bytes("GHOME",encoding="utf-8"))
    print("准备移动到装配点")
    time.sleep(1)
    
    
    #等待设备到装配点,安装设备
    ret = str(conn.recv(1024),encoding="utf-8")
    print(ret)
    error_dct(ret,'HOMED')
    print('IMU标定完成')
    conn.close()