# -*- coding: utf-8 -*
import socket
import time
import threading
import sys
import base64
config = {}
with open("wrc-client-config.dict","r") as config_handle:
    config = eval(config_handle.read().strip("\n"))
print("[INFO] config =",config)
wrcs = socket.socket()
oa = False
if len(sys.argv) < 2:
    host = input("[Client] 请输入目标主机:")
    port = input("[Client] 请输入目标端口(默认应为7201):")
    print("[Client] 请选择连接方式:")
    print("w - 公网")
    print("l - 内网")
    print("c - 自定义IP")
    print("d - 调试模式(localhost)")
    iptype = input("请选择:")
else:
    oa = True
    host = sys.argv[1]
    port = sys.argv[2]
    iptype = sys.argv[3]
lsprint = True
executed = True
ip = ""
if iptype:
    if iptype == "w":
        if not oa: 
            ip = socket.gethostbyname(input("暂不支持获取公网IP\n请手动输入公网IP:"))
        else:
            ip = socket.gethostbyname(sys.argv[4])
    if iptype == "l":
        ip = socket.gethostbyname(socket.gethostname())
    if iptype == "c":
        if not oa: 
            ip = socket.gethostbyname(input("请输入自定义IP:"))
        else:
            ip = socket.gethostbyname(sys.argv[4])
    if iptype == "d":
        ip = "127.0.0.1"
else:
    ip = "127.0.0.1"
wrcs.connect((host,int(port)))
wrcr = socket.socket()
wrcr.bind((config["listen_address"],config["listen_port"]))
wrcr.listen()
print("[Client] 接收端已启动("+str(config["listen_port"])+")...")
if config["reporting"]:
    print("[Client] 上报连接中...")
    reporter = socket.socket()
    reporter.connect((config["report_address"],config["report_port"]))
    def report(content,cttype="info",owner="Main"):
        global reporter
        content = bytes.decode(base64.b64encode(content.encode("utf-8")),encoding="utf-8")
        reporter.send(str(cttype+"/"+owner+"/"+content).encode("utf-8"))
    report("Reporter Connected")
    print("[Client] 上报连接成功")
else:
    print("[Client] 上报已禁用")
    def report(content,cttype="info",owner="Main"):
        print("[Client] [Warning] 已阻止上报:",owner,"->",cttype,"->",bytes.decode(base64.b64encode(content.encode("utf-8")),encoding="utf-8"))
wrcs.send(ip.encode("utf-8"))
while True:
    wconn, wadr = wrcr.accept()
    data = wconn.recv(1024)
    if data:
        print(bytes.decode(data,encoding="utf-8"))
        report("Server Connected")
        break
localexec = socket.socket()
lestop_signal = False
def localexec_thread():
    global lestop_signal
    # print("[LocalExec] 外部输入线程已启动")
    # print("[LocalExec] 外部输入连接中")
    localexec = socket.socket()
    localexec.bind((config["localexec_address"],config["localexec_port"]))
    localexec.listen()
    # print("[LocalExec] 外部输入监听中...")
    localexec_record = ""
    lconn, ladr = localexec.accept()
    while True:
        try:
            data = lconn.recv(1024)
        except:
            break
        if data:
            try:
                # print(bytes.decode(data,encoding="utf-8"))
                # print("[LocalExec] 接收外部输入:",bytes.decode(data,encoding="utf-8"))
                if not config["get_full_localexec"]:
                    serverexec(bytes.decode(data,encoding="utf-8"))
                else:
                    localexec_record += bytes.decode(data,encoding="utf-8").replace("#EXECUTE","")
                    if "#EXECUTE" in bytes.decode(data,encoding="utf-8"):
                        serverexec(localexec_record)
                        localexec_record = ""
            except Exception as e:
                # print("[LocalExec] [ERROR] 解码数据失败\nCaused By:")
                # print(e)
                pass
        lconn.send(data.upper())
        time.sleep(0.2)
        if lestop_signal:
            break
    print("[LocalExec] 外部输入线程已关闭")
if config["localexec"]:
    threading.Thread(target=localexec_thread).start()
    print("[LocalExec] 外部输入线程已启动")
print("Socket已连接->"+host+":"+port)
def wrecv():
    global wconn
    global config
    global executed
    global lsprint
    while True:
        try:
            data = wconn.recv(1024)
        except:
            break
        if data:
            if lsprint:
                try:
                    print(bytes.decode(data,encoding="utf-8").replace("@EXECUTED",""))
                    report(bytes.decode(data,encoding="utf-8"),cttype="data",owner="Receiver")
                    if config["get_full_data"] and "@EXECUTED" in bytes.decode(data,encoding="utf-8"):
                        report("Command Result Received Successful",owner="Receiver")
                        break
                except Exception as e: 
                    print("[Client] [ERROR] 解码数据失败\nCaused By:")
                    print(e)
                    report(str(e),cttype="error",owner="Receiver")
                if not config["get_full_data"]:
                    break
            else:
                report("Receiver Thread Died",cttype="warn",owner="Receiver")
                break
        wconn.send(data.upper())
        time.sleep(0.1)
    executed = True
def wsend(line):
    global wrcs
    global wrcr
    global wconn
    global config
    global executed
    global lsprint
    line = line.split(" ")
    del(line[0])
    wrcs.send(" ".join(line).encode("utf-8"))
    report("Command Sent Successful",owner="Sender")
    timer = 0
    executed = False
    lsprint = True
    receiver = threading.Thread(target=wrecv)
    receiver.start()
    while True:
        timer += 1
        if timer > config["listen_timeout"] * 10:
            print("[Client] [Warning] 监听线程已超时(>"+str(config["listen_timeout"])+"s)")
            report("Receiver Thread Timed Out",owner="Receiver")
            executed = True
        if executed == True:
            lsprint = False
            break
        time.sleep(0.1)
break_signal = False
def serverexec(line):
    global wrcs
    global wrcr
    global config
    global break_signal
    if line == "help":
        print("============ Commands Help ============")
        print("help - 显示帮助")
        print("send - 发送数据")
        print("close - 关闭连接")
        print("config - 修改配置")
    elif line == "close":
        wrcs.close()
        wrcr.close()
        break_signal = True
    elif line == "pass":
        wsend("send echo.")
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
                report("Config Writed",owner="Configurator")
            elif args[0] == "set":
                try:
                    config[line.split(" ")[2]] = eval(line.split(" ")[3])
                    print("配置修改完成")
                    report("Config Edited Successful",owner="Configurator")
                except Exception as e:
                    print("配置修改失败\nCaused By:\n",e)
                    report("Config Edited Failed",cttype="error",owner="Configurator")
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
while True:
    line = input(">")
    serverexec(line)
    if break_signal:
        break

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
report("Client Closing")
if config["reporting"]:
    reporter.close()
    print("[Client] 上报连接已关闭")
if config["localexec"]:
    lestop_signal = True
    time.sleep(0.3)
    localexec.close()
print("[Client] 连接已关闭")