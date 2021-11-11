from logging import fatal
import psutil
import datetime
import time
import json
from win10toast import ToastNotifier
from multiprocessing import Process

toaster = ToastNotifier()
def notify(title, content, duration):
    toaster.show_toast(title,
        content,
        icon_path=None,
        duration=duration,
        threaded=True)
if __name__ == '__main__':
    totalTime = 0
    todayTime = {}
    programTime = {}
    lastAttetionTime = {}
    with open("./config.json") as load_f:
        configDict = json.load(load_f)
    setTime = configDict['time'] * 60
    while(1):
        start = time.perf_counter()
        tmp = {}
        flag = False
        # 遍历进程
        for i in psutil.process_iter():
            # 找到指定进程
            if i.name() in configDict['programs']:
                # 是否是刚开始，直接杀死进程
                time1 = datetime.datetime.fromtimestamp(int(i.create_time()))
                time2 = datetime.datetime.now()
                if ((time2-time1).seconds < 10 and setTime - totalTime < configDict['thresholdTime'] * 60):
                    # 通知用户
                    notify("时间不足", "您今日可玩时间只剩"+str(round(((setTime-totalTime)/60),2))+'分钟,因此强制结束进程', 15)
                    i.terminate()
                # 记录开始时间
                tmp[i.name()] = i.create_time()
                # 持续游戏时间过长提醒
                if ((time2-time1).seconds > configDict['runOnTime'] * 60):
                    if (i.name() in lastAttetionTime.keys() and (time2-lastAttetionTime[i.name()]).seconds > 300) or i.name() not in lastAttetionTime.keys():
                        lastAttetionTime[i.name()] = time2
                        notify("游玩时间过长", "您已经持续玩游戏"+str(round(((time2-time1).seconds/60),2))+'分钟,注意休息', 15)
        for k in programTime.keys():
            if k not in tmp.keys():
                time1 = datetime.datetime.fromtimestamp(int(programTime[k]))
                time2 = datetime.datetime.now()
                if k not in todayTime.keys():
                    todayTime[k] = (time2-time1).seconds
                else:
                    todayTime[k] += (time2-time1).seconds
        programTime = tmp
        end = time.perf_counter()
        # time.sleep(start+60-end)