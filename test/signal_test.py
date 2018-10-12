
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    监听了SIGINT信号, 当程序在运行的时候同时按下键盘 Ctrl+c 就会输出
    收到信号 2 <frame object at 0x00000000021DD048>
    handler方法的两个参数分别是 信号编号, 程序帧
"""

import sys
import time
import os
import signal

receive_times = 0

def handler(signalnum, handler):
    global receive_times
    print ("收到信号", signalnum, frame, receive_times)
    receive_times += 1
    if receive_times > 3:
        exit(0) # 自己走

def main():
    signal.signal(signal.SIGINT, handler) # Ctrl-c
    # time.sleep(10) # SIGINT 信号同样能唤醒 time.sleep, 所以这里程序就会结束
    while True: # 改成 while 效果会好点
       pass

if __name__ == '__main__':
    main()