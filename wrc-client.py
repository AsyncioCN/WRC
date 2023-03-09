# -*- coding: utf-8 -*
import socket
import time
config = {}
with open("wrc-client-config.dict","r") as config_handle:
    config = eval(config_handle.read().strip("\n"))
print("[INFO] config =",config)
wrcs = socket.socket()
host = input("[Client] 请输入目标主机:")
port = input("[Client] 请输入目标端口(默认应为7201):")
print("[Client] 请选择连接方式:")
print("w - 公网")
print("l - 内网")
print("c - 自定义IP")
print("d - 调试模式(localhost)")
iptype = input("请选择:")
ip = ""
if iptype:
    if iptype == "w":
        ip = socket.gethostbyname(input("暂不支持获取公网IP\n请手动输入公网IP:"))
    if iptype == "l":
        ip = socket.gethostbyname(socket.gethostname())
    if iptype == "c":
        ip = socket.gethostbyname(input("请输入自定义IP:"))
    if iptype == "d":
        ip = "127.0.0.1"
else:
    ip = "127.0.0.1"
wrcs.connect((host,int(port)))
wrcr = socket.socket()
wrcr.bind((config["listen_address"],config["listen_port"]))
wrcr.listen()
print("[Client] 接收端已启动(7200)...")
wrcs.send(ip.encode("utf-8"))
while True:
    wconn, wadr = wrcr.accept()
    data = wconn.recv(1024)
    if data:
        print(bytes.decode(data,encoding="utf-8"))
        break
print("Socket已连接->"+host+":"+port)
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
            if args[0] == "help":
                print("此命令的语法是:")
                print("\t显示帮助 config help")
                print("\t显示配置 config list")
                print("\t保存配置 config save")
                print("\t修改配置 config set <key> <expression>")
            elif args[0] == "list":
                print("当前配置:")
                for key in config:
                    print(key,"=",config[key]," => ",type(config[key]))
            elif args[0] == "save":
                print("正在写入配置 -> wrc-client-config.dict")
                content = ""
                with open("wrc-client-config.dict","w") as config_handle:
                    content += "{"
                    for key in config:
                        if type(config[key]) == str:
                            item = "\""+config[key]+"\""
                        else:
                            item = str(config[key])
                        content += "\n\t\""+key+"\":"+item+","
                    content += "\n}"
                    config_handle.write(content)
                    config_handle.close()
                print("配置文件写入完成")
            elif args[0] == "set":
                try:
                    config[line.split(" ")[2]] = eval(line.split(" ")[3])
                    print("配置修改完成")
                except Exception as e:
                    print("配置修改失败\nCaused By:\n",e)
            else:
                print("命令语法不正确\n请使用\"config help\"显示此命令的帮助")
        else:
            print("命令语法不正确\n请使用\"config help\"显示此命令的帮助")
    else:
        if config["default_send"]:
            wsend("send "+line)
        else:
            print("未定义的命令:",line.split(" ")[0],"\n你是指“send",line,"”吗？")
            print("请使用config default_send True开启默认发送")
if config["write_config"]:
    print("[Client] 正在写入配置 -> wrc-client-config.dict")
    content = ""
    with open("wrc-client-config.dict","w") as config_handle:
        content += "{"
        for key in config:
            if type(config[key]) == str:
                item = "\""+config[key]+"\""
            else:
                item = str(config[key])
            content += "\n\t\""+key+"\":"+item+","
        content += "\n}"
        config_handle.write(content)
        config_handle.close()
    print("[Client] 配置文件写入完成")
print("[Client] 连接已关闭")