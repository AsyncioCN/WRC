# -*- coding: utf-8 -*
import socket
import time
wrcs = socket.socket()
host = input("[Client] 请输入目标主机:")
port = input("[Client] 请输入目标端口(默认应为7201):")
wrcs.connect((host,int(port)))
wrcr = socket.socket()
wrcr.bind(("0.0.0.0",7200))
wrcr.listen()
print("[Client] 接收端已启动(7200)...")
wrcs.send(socket.gethostbyname(socket.gethostname()).encode("utf-8"))
while True:
    wconn, wadr = wrcr.accept()
    data = wconn.recv(1024)
    if data:
        print(bytes.decode(data,encoding="utf-8"))
        break
print("Socket已连接->"+host+":"+port)
config = {
    "listen_timeout":10,
    "default_send":False
}
def wsend(line):
    global wrcs
    global wrcr
    global wconn
    global config
    line = line.split(" ")
    del(line[0])
    wrcs.send(" ".join(line).encode("utf-8")) #发送命令
    # wconn, wadr = wrcr.accept() #？
    timer = 0 #重置计数器
    while True:
        # wconn, wadr = wrcr.accept() #？
        try:
            data = wconn.recv(1024) #尝试接收数据
        except:
            break
        if data:
            try:
                print(bytes.decode(data,encoding="utf-8")) 
            except Exception as e: 
                print("[Client] [ERROR] 解码数据失败\nCaused By:")
                print(e)
            break #跳出数据接收while
        wconn.send(data.upper())
        time.sleep(0.2) 
        timer += 1
        # print("[DEBUG] timer=",time,"\tlisten_timeout=",config["listen_timeout"])
        if timer > config["listen_timeout"] * 5:
            print("[Client] [INFO] 接收数据超时")
            break
while True:
    line = input(">")
    if line == "help":
        print("============ Commands Help ============")
        print("help - 显示帮助")
        print("send - 发送数据")
        print("close - 关闭连接")
        print("config - 修改配置")
    elif line == "close":
        wrcs.close()
        wrcr.close()
        break
    elif line.split(" ")[0] == "send": #如果命令为发送
        wsend(line)
    elif line.split(" ")[0] == "config":
        args = line.split(" ")
        if type(args) == list and len(args) > 1:
            del(args[0])
            if args[0] == "list":
                print("当前配置:")
                for key in config:
                    print(key,"=",config[key]," => ",type(config[key]))
            else:
                try:
                    config[line.split(" ")[1]] = eval(line.split(" ")[2])
                    print("配置修改完成")
                except Exception as e:
                    print("配置修改失败\nCaused By:\n",e)
        else:
            print("命令语法错误")
    else:
        if config["default_send"]:
            wsend("send "+line)
        else:
            print("未定义的命令:",line.split(" ")[0],"\n你是指“send",line,"”吗？")
            print("请使用config default_send True开启默认发送")
print("[Client] 连接已关闭")