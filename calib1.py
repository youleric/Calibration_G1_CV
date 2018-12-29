# coding:utf-8
import os
import time
import datetime
import socket
import yaml
import numpy as np

#初始化设备-宏定义
dutpath = '/storage/emulated/0/Android/data/com.tmac.camerapreview/files'
no = ['0','0000033330000','0000066660000','0000100000000','0000133330000','0000166660000','0000200000000','0000233330000','0000266660000','0000300000000','0000333330000','0000366660000','0000400000000','0000433330000','0000466660000','0000500000000','0000533330000','16','17','18','19','20','21','22','23','24','25']
phase_enable = ['0','1','1','1']

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

 
# 定义要创建的目录
path="/home/zyt/WorkSpace/calibration_data/"+str(devices[0])+"/"


# 创建标定文件夹到定义目录
path=path.strip()
path=path.rstrip("/")
isExists=os.path.exists(path)
if not isExists:
    os.makedirs(path) 
    print('标定数据目录 '+path+' 创建成功')
else:
    print(path+' 目录已存在')
    os.system('rm -r '+path)
    print('删除目录中')
    time.sleep(5)
    os.makedirs(path)
    print('标定数据目录 '+path+' 创建成功')



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
    time.sleep(20)
    f = os.popen(r"adb shell testimucal 1", "r")
    shuchu = f.read()
    f.close()
    print("IMU标定1结果"+shuchu)
    conn.sendall(bytes("P1S2S",encoding="utf-8"))
    print("准备移动到下一个点")
    
    
    #获取标定数据-P1S2S-IMU标定步骤2
    ret = str(conn.recv(1024),encoding="utf-8")
    print(ret)
    print("已移动到机械臂IMU标定2号点，开始2位置标定")
    time.sleep(20)
    f = os.popen(r"adb shell testimucal 2", "r")
    shuchu = f.read()
    f.close()
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
    print("IMU标定3结果"+shuchu)
    conn.sendall(bytes("GHOME",encoding="utf-8"))
    print("准备移动到装配点")
    time.sleep(1)
    
    
    #等待设备到装配点,安装设备
    ret = str(conn.recv(1024),encoding="utf-8")
    print(ret)
    error_dct(ret,'HOMED')
    while True:
        print('请调换眼镜设备方向,调换后输入jx继续下一步')
        input_data=input('>>: ').strip()
        if len(input_data) == 0:continue
        if input_data == 'jx': break


#获取标定数据-P2S1S-IMU-FE内外参标定准备
if phase_enable[1]=='1':
    os.chdir(path)
    conn.sendall(bytes("P3S1S",encoding="utf-8"))
    print("准备移动到机械臂IMU-FE内外参标定点")
    time.sleep(1)
    ret = str(conn.recv(1024),encoding="utf-8")
    print(ret)
    if ret != 'P3S1E': 
        print('机械臂返回错误，请检查后重试')
        exit()
    print("已移动到机械臂IMU-FE内外参标定点，开始标定")
    time.sleep(1)
    conn.sendall(bytes("P2S1S",encoding="utf-8"))
    print("准备移动到机械臂IMU-FE内外参标定点")



    #获取标定数据-P2S1S-IMU-FE内外参标定
    print("已移动到机械臂IMU-FE内外参标定点，开始标定")
    os.system('adb shell rm -rf /sdcard/cv_data_save')
    time.sleep(1)
    os.system('adb shell setprop debug.cv.save.data 4')
    time.sleep(1)
    foff = os.popen(r"adb shell slamclienttest", "r")
    time.sleep(1)
    ret = str(conn.recv(1024),encoding="utf-8")
    print(ret)
    if ret != 'P2S1E': exit()
    os.system('adb shell setprop debug.cv.save.data 0')
    time.sleep(1)
    os.system('adb pull /sdcard/cv_data_save/ '+path)
    time.sleep(1)
    print('数据已保存')
    


#获取标定数据-P3-静态内外参标定
if phase_enable[2]=='1':
    conn.sendall(bytes("P3S1S",encoding="utf-8"))
    print("准备移动到下一个点")
    time.sleep(1)
    x = 1
    while (x<16) :
        ret = str(conn.recv(1024),encoding="utf-8")
        print(ret)
        print("已移动到机械臂静态内外参标定点，开始标定")
        print('P3位置'+str(x)+'数据开始采集')
        n = ''
        while (n!="rgbPic.jpg\n") :
            os.system('adb shell am start -n com.tmac.camerapreview/com.tmac.camerapreview.TwoCamera')
            time.sleep(6)
            f = os.popen(r"adb shell ls /storage/emulated/0/Android/data/com.tmac.camerapreview/files/rgb/", "r")
            n = f.read()
            f.close()
        os.system('adb shell mv '+dutpath+'/fisheye/fisheyePic.jpg '+dutpath+'/fisheye/'+no[x]+'.jpg')
        os.system('adb shell mv '+dutpath+'/rgb/rgbPic.jpg '+dutpath+'/rgb/'+no[x]+'.jpg')
        time.sleep(1)
        os.system('adb pull /storage/emulated/0/Android/data/com.tmac.camerapreview/files '+path)
        time.sleep(1)
        print('P3位置'+str(x)+'数据已保存')
        if x<10 :
            senddata = "P3S"+str(x)+"S"
        if x>9 :
            senddata = "3S"+str(x)+"S"
        conn.sendall(bytes(senddata,encoding="utf-8"))
        print("准备移动到下一个点")
        os.system('adb shell rm -r /storage/emulated/0/Android/data/com.tmac.camerapreview/files')
        time.sleep(1)
        x=x+1

 
#结束标定，回到初始位置 
if phase_enable[3]=='1':
	ret = str(conn.recv(1024),encoding="utf-8")
	print(ret)
	time.sleep(1)
	conn.sendall(bytes("GHOME",encoding="utf-8"))
	print("准备移动到装配点")
	time.sleep(1)
	ret = str(conn.recv(1024),encoding="utf-8")
	print(ret)
	error_dct(ret,'HOMED')
	print(datetime.datetime.now())
	conn.close()
	print('数据已保存')
	print('标定获取数据结束')
	print('开始执行参数计算')


# 定义工作目录
path="/home/zyt/WorkSpace/calibration_data/"+str(devices[0])+"/"
kalibpath="/home/zyt/kalibr/"


#开始处理IMU-FE数据标定
os.chdir(path)
os.system('mkdir cam-imu')
time.sleep(1)
isExists=os.path.exists(path)
if isExists:
	print('cam-imu目录已创建成功')
else:
	print('cam-imu目录未创建')
	print('请重新开始')
	exit()
os.system('mv cam0 cam-imu')
os.system('mv data.csv cam-imu/imu0.csv')
os.system('mv loop01.txt cam-imu/cameraindex.csv')
os.system('cp '+kalibpath+'kal_imu.sh kal_imu.sh')
os.system('cp '+kalibpath+'imu_lenovo.yaml imu_lenovo.yaml')
os.system('cp '+kalibpath+'april_6x6.yaml april_6x6.yaml')
os.system('chmod a+x kal_imu.sh')
print(datetime.datetime.now())
os.system('./kal_imu.sh')

print(datetime.datetime.now())

#开始处理IMU-FE数据标定
f = open("results-imucam-glasses.txt","r")   #设置文件对象
data = f.readlines()  #直接将文件中按行读到list里，效果与方法2一样
f.close()             #关闭文件
print(data[37])

distor = data[37]
distor = distor.split("[")
distor = distor[1].split("]")
distor = distor[0].split(",")

focal=data[34]
focal=focal.split("[")
focal=focal[1].split("]")
focal=focal[0].split(",")

princ=data[35]
princ=princ.split("[")
princ=princ[1].split("]")
princ=princ[0].split(",")



if (data[15][2]=='-'):
    trans1='['+data[15][2:13]+', '+data[15][14:25]+', '+data[15][26:37]+', '
elif (data[15][2]==' '):
    trans1='['+data[15][3:13]+', '+data[15][14:25]+', '+data[15][26:37]+', '
    
if (data[16][2]=='-'):
    trans2='          '+data[16][2:13]+', '+data[16][14:25]+', '+data[16][26:37]+', '
elif (data[16][2]==' '):
    trans2='          '+data[16][3:13]+', '+data[16][14:25]+', '+data[16][26:37]+', '

if (data[17][2]=='-'):
    trans3='          '+data[17][2:13]+', '+data[17][14:25]+', '+data[17][26:37]+']'
elif (data[17][2]==' '):
    trans3='          '+data[17][3:13]+', '+data[17][14:25]+', '+data[17][26:37]+']'

if (data[15][2]=='-'):
    rotate='['+data[15][38:49]+', '+data[16][38:49]+', '+data[17][38:49]+']'
elif (data[15][2]==' '):
    rotate='['+data[15][39:49]+', '+data[16][38:49]+', '+data[17][38:49]+']'

trans=trans1+'\n'+trans2+'\n'+trans3+'\n'

timeshift=data[21]
timeafter=float(timeshift)*1000000000  

write_data='%YAML:1.0'+'\n'+'\n'+'model_type: KANNALA_BRANDT'+'\n'+'camera_name: fisheye002'+'\n'+\
'image_width: 640'+'\n'+'image_height: 480'+'\n'+'projection_parameters:'+'\n'+'   k2: '+str(distor[0])\
+'\n'+'   k3:'+str(distor[1])+'\n'+'   k4:'+str(distor[2])+'\n'+'   k5:'+str(distor[3])+'\n'+'   mu: '+\
str(focal[0])+'\n'+'   mv:'+str(focal[1])+'\n'+'   u0: '+str(princ[0])+'\n'+'   v0:'+str(princ[1])+'\n'+\
'extrinsicRotation: !!opencv-matrix'+'\n'+'   rows: 3'+'\n'+'   cols: 3'+'\n'+'   dt: d'+'\n'+'   data: '\
+trans+'\n\n'+'extrinsicTranslation: !!opencv-matrix'+'\n'+'   rows: 3'+'\n'+'   cols: 1'+'\n'+'   dt: d'+'\n'\
+'   data: '+rotate+'\n\n'+'noise_acc: 0.4 #0.4'+'\n'+'noise_gyr: 0.06 #0.06'+'\n'+'rwalk_acc: 0.0003 #0.0003'\
'\n'+'rwalk_gyr: 0.002 #0.002'+'\n'+'grav_norm: 9.81007'+'\n\n'+'device_type: "sunflower"'+'\n'\
+'\n'+'loopC_pattern: "/etc/SleLnoAvoM/loopC_pattern.yml"'+'\n'+\
'loopC_vocdata: "/etc/SleLnoAvoM/loopC_vocdata.bin"'+'\n'+'svm_file: "/etc/SleLnoAvoM/svm.xml"'+'\n'\
'feat_extract_thr: 240'+'\n'+'imu_image_t_offset: '+str(timeafter)+'\n'+'pose_graph_load: 1'+'\n'+\
'pose_graph_save: 1'+'\n\n'+'stable_mode: 0'+'\n\n'+'DEBUG_SAVE_FILE: 0'

fnew = open("config_sunflower.yaml", "w")
fnew.write(write_data)
fnew.close()

print('IMU-FE标定数据标定成功')
print('开始标定RGB-FE数据')
	
print(datetime.datetime.now())
os.system('mv cam-imu cam-imu-0')
os.system('rm -r glasses.bag camchain-glasses.yaml report-cam-glasses.pdf report-imucam-glasses.pdf results-cam-glasses.txt')
time.sleep(5)
os.system('mkdir cam-imu')
os.system('mv rgb cam-imu/cam1')
os.system('mv fisheye cam-imu/cam0')
os.system('cp '+kalibpath+'kal_rgb.sh kal_rgb.sh')
os.system('cp '+kalibpath+'cameraindex.csv cam-imu/cameraindex.csv')


os.system('./kal_rgb.sh')

print(datetime.datetime.now())
print(datetime.datetime.now())

print('计算RGB和IMU外参')
	
#FE to RGB
f1 = open(r"camchain-glasses.yaml")
x1 = yaml.load(f1)
data1=np.mat(np.zeros((4,4)))
n=0
while(n<4):
	m=0
	while(m<4):
		data1[n,m]=x1['cam1']['T_cn_cnm1'][n][m]
		m=m+1		
	n=n+1
f1.close()


#imu to FE
f2 = open(r"camchain-imucam-glasses.yaml")
x2 = yaml.load(f2)
data2=np.mat(np.zeros((4,4)))
n=0
while(n<4):
	m=0
	while(m<4):
		data2[n,m]=x2['cam0']['T_cam_imu'][n][m]
		m=m+1		
	n=n+1
f2.close()

data3=np.dot(data1.I,data2.I)

write_data="{\"Data\":["
n=0
while(n<3):
	m=0
	while(m<4):
		write_data=write_data+str(data3[n,m])+','
		m=m+1		
	n=n+1

write_data=write_data+str(data3[3,0])+','+str(data3[3,1])+','+str(data3[3,2])+','+str(data3[3,3])+']}'
print(write_data)
fnew = open("rgbtoimu.txt", "w")
fnew.write(write_data)
fnew.close()



print('写入标定数据到设备')
os.system('adb push rgbtoimu.txt /persist/sensors')
os.system('adb push config_sunflower.yaml /persist/sensors')
os.system('adb push camchain-glasses.yaml /persist/sensors')
os.system('adb push camchain-imucam-glasses.yaml /persist/sensors')
os.system('adb push results-imucam-glasses.txt /persist/sensors')

print('标定过程全部完成，请继续标定下一台设备')
print(datetime.datetime.now())

'''
位置说明
GHONE 1 装配点
P1S1S 2 IMU位置1
P1S2S 3 IMU位置2
P1S3S 4 IMU位置3
P2S1S 5 IMU-FE内外参标定流程
P3S1S 6 静态内外参标定初始位置1
P3S2S 7 静态内外参标定位置左1
'''
