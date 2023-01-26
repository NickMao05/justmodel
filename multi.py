import time,os,signal,sys,atexit
import subprocess
import os
import sys
import importlib.util
import shlex
import platform
import argparse
import json

# from atexit import register

pidfile = "/tmp/netkiller.pid"
logdir = "/tmp"
logfile = logdir+"/netkiller.log"
logger = None
loop = True
job = True

# 保存进程ID
def savepid(pid):
    with open(pidfile, 'w') as f:
        f.write(str(os.getpid()))
    # 注册退出函数，进程退出时自动移除pidfile文件
    atexit.register(os.remove, pidfile)
# 从pidfile中读取进程ID
def getpid():
    pid = 0
    try:
        with open(pidfile, 'r') as f:
            pid = int(f.readline())
    except FileNotFoundError as identifier:
        print(identifier)
    # print(pid)
    return pid

# 创建日志
def createlog():
    global logger
    logger = open(logfile,mode="a+")
    return logfile
# 写入日志
def log(level,msg):
    logger.write(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()) + " "+level+" "+ msg +"\r\n")
    logger.flush()

# 信号处理
def signalHandler(signum,frame):
    global loop,job
    # print("SIGN ",str(signum));
    if signum == signal.SIGHUP :
        # 优雅重启
        job = False
        # print("WARN","优雅重启完毕\r\n")
    elif signum == signal.SIGINT:
        # 正常退出
        loop = False
        job = False
        # print("WARN","正常退出 \r\n")
    elif signum == signal.SIGUSR1:
        # 日志切割
        job = False
        dst = time.strftime(logdir + "/netkiller-%Y-%m-%d.%H-%M-%S.log",time.localtime());
        os.rename(logfile, dst)

def daemonize():
    global job 

    signal.signal(signal.SIGHUP, signalHandler)
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGUSR1, signalHandler)
    signal.alarm(5)

    pid = os.fork()
    sys.stdout.flush()
    sys.stderr.flush()
    if pid :
        sys.exit(0)
    # print(os.getpid())
    savepid(str(os.getpid()))
    while loop :
        createlog()
        log("WARN","Start!!!")
        while job:
            main()
            # log("DEBUG",str(loop) + "|" + str(job))
        log("WARN","Exit!!!")
        job = True
        logger.flush()
        logger.close()

def start():
    if os.path.isfile(pidfile) :
        print("error")
        sys.exit(1)
    else:
        daemonize()

def stop():
    try:
        os.kill(getpid(), signal.SIGINT) 
    except ProcessLookupError as identifier:
        print(identifier)
    # os.remove(pidfile)

def reloads():
    try:
        os.kill(getpid(), signal.SIGHUP) 
    except ProcessLookupError as identifier:
        print(identifier)

def logrotate():
    try:
        os.kill(getpid(), signal.SIGUSR1) 
    except ProcessLookupError as identifier:
        print(identifier)

def main():
    # 业务逻辑
    os.environ['REQS_FILE'] = 'requirements.txt'
    os.environ['COMMANDLINE_ARGS'] = '--no-half-vae --port 33897 --ngrok 2K95gmylUQ7mztGzNeIPK6h1oI0_3AZs2je3o12Ai8d2qj1PU --enable-insecure-extension-access --localizations-dir /kaggle/working/stable-diffusion-webui/localizations/  --deepdanbooru --disable-safe-unpickle'
    os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
    exec(open("launch.py").read())
    # 业务逻辑
    time.sleep(2)

def usage():
    print(sys.argv[0] + " start | stop | restart | reload | log")

if __name__ == "__main__":
    # print(sys.argv)
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "start" :
            start()
        elif arg == "stop":
            stop()
        elif arg == "restart" :
            stop()
            start()    
        elif arg == "reload":
            reloads()
        elif arg == "log":
            logrotate()    
        else:
            usage()
    else: 
        usage()
