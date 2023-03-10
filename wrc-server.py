# -*- coding: utf-8 -*
import socket
import subprocess
import sys
import asyncio
import time
config = {}
with open("wrc-server-config.dict","r") as config_handle:
    config = eval(config_handle.read().strip("\n"))
print("[INFO] config =",config)
commander_ip = ""
rlogined = False
sender = socket.socket()
async def run(cmd):
    global rlogined
    global commander_ip
    if rlogined == False:
        sender.connect((cmd,config["sendback_port"]))
        sender.send(str("[INFO] IP Loged ->"+cmd).encode("utf-8"))
        print("[INFO] Loged Commander IP ->"+cmd)
        commander_ip = cmd
        rlogined = True
    else:
        cmd_result = subprocess.getoutput("shell.cmd "+cmd)
        print("[SubProccess] [INFO] Command Executed.\n[SubProccess]\n"+cmd_result)
        print("[SubProccess] [INFO] Sending Result ->"+commander_ip)
        try:
            sender.send(cmd_result.encode("utf-8"))
            time.sleep(0.2)
            sender.send("@EXECUTED".encode("utf-8"))
        except Exception as e:
            print("[SubProccess] [ERROR] Exception In SubProccess\n"+str(e))
while True:
    rlogined = False
    client = socket.socket()
    sender = socket.socket()
    client.bind((config["listen_address"],config["listen_port"]))
    client.listen()
    print("[Client] Listening...")
    conn, adr = client.accept()
    while True:
        try:
            data = conn.recv(1024)
        except:
            break
        if data:
            print("[INFO] Recieved Command:"+bytes.decode(data))
            asyncio.run(run(bytes.decode(data)))
        conn.send(data.upper())
        time.sleep(0.2)
    print("[Client] Listener Closed")
    client.close()
    sender.close()
    if config["relaunch"]:
        print("[Client] Listener Relaunch in "+str(config["relaunch_timeout"])+"s...")
        time.sleep(config["relaunch_timeout"])
    else:
        break