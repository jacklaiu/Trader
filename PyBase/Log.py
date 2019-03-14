#coding: utf-8
import Util as util

def log(content):
    string = "[Time: " + util.getYMDHMS() + "]: " + str(content)
    print(string)
    file = open("log.out", "a")
    file.write(string + "\n")
    file.close()
    return string

def consoleLog(logtype="运行中", content="没有内容"):
    string = str(logtype) + " [" + util.getYMDHMS() + "]: " + str(content)
    print(string)