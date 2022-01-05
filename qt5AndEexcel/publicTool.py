
#!/usr/bin/env python3
# coding=utf-8
__author__ = 'Jianggb'
import os,sys,re
from PublicLogTool import logger
from ispaceTool import SpaceName
countInfo = {}
countFiles = []
transFiles = []

def 蓝(content):
    return '<font color="#0000FF">' + content +'</font>'
def 红(content):
    return '<font color="#FF0000">' + content +'</font>'
def 绿(content):
    return '<font color="#00FF00">' + content +'</font>'
def 黄(content):
    return '<font color="#FFFF00">' + content +'</font>'
def 青(content):
    return '<font color="#00FFFF">' + content +'</font>'
def 橙(content):
    return '<font color="#FF8000">' + content +'</font>'
def 紫(content):
    return '<font color="#FF00FF">' + content +'</font>'

mdidType  = "20000" #人工定义对象类
objidType = "10000" #具体对象
type0Type = "00000" #对象类
qsType    = "?0000" #ID?
rfType    = "*0000" #ID*
QidType   = "Q0000" #对象类全集
SidType   = "S0000" #对象类子集
XidType   = "X0000" #对象类某种
xidType   = "x0000" #对象类某个

def GetMtype(mId):
    #logger.info("GetMtype mid:%s type:%s"%(mId, mId[0:16]))
    return str(mId)[0:5]

def isMid(val) -> bool:
    "判断字符串是否是mid"
    if len(str(val)) != 18:
        return False
    if re.match('[?*0-9A-Za-z][A-Za-z0-9]{5}', val[0:6]) == None:
        return False
    if re.match('[0-9a-f]{8}', val[6:14]) == None:
        return False
    if re.match('[0-9a-f]{4}', val[14:]) == None:
        return False
    return True

def is0Type(mId):
    "是否是对象类"
    if GetMtype(mId) == type0Type or GetMtype(mId) == QidType \
        or GetMtype(mId) == SidType or GetMtype(mId) == XidType\
        or GetMtype(mId) == SidType:
        return True
    return False

def isMtypeRoot(mId):
    "根节点类型"
    if mId and not is0Type(mId) and GetMtype(mId) != qsType \
        and GetMtype(mId) != rfType and GetMtype(mId) != objidType \
        and isMid(mId) and GetMtype(mId) != mdidType:
        return True
    return False

def colorValStr(instr):
    "染色"
    if isMtypeRoot(instr):
        return 红(instr)
    elif isMid(instr):
        return 青(instr)
    elif instr in SpaceName._member_map_.keys():
        return 紫(instr)
    else:
        return 蓝(instr)

def colorKeyStr(instr:str):
    "染色"
    if isMtypeRoot(instr) or instr.upper() == "ERROR":
        return 红(instr)
    elif isMid(instr):
        return 红(instr)
    else:
        return 青(instr)

def buildColorTxt(inobj, num=0):
    "格式化"
    ret = ""
    plat = sys.platform
    idt = 2
    if plat == 'linux':
        idt = 4
    preSpace = "&nbsp;"*idt*num #缩进
    if isinstance(inobj, str) or isinstance(inobj, int) or\
        isinstance(inobj, float) or isinstance(inobj, tuple):
        ret += colorValStr(inobj) + ","
    elif isinstance(inobj, list):
        ret += "<br>" + preSpace + "["
        nkey = 0
        for obj in inobj:
            if nkey == 0:
                ret += buildColorTxt(obj, num+1) + ","
            else:
                ret += "<br>" + preSpace + buildColorTxt(obj, num+1) + ","
            nkey += 1
        if nkey == 1:
            ret += "],"
        else:
            ret += "<br>" + preSpace + "],"
    elif isinstance(inobj, dict):
        ret += "<br>" + preSpace + "{"
        nkey = 0
        for key in inobj:
            if nkey == 0:
                ret += colorKeyStr(key) + ":" + buildColorTxt(inobj[key], num+1) + ","
            else:
                ret += "<br>" + preSpace + colorKeyStr(key) + ":" + buildColorTxt(inobj[key], num+1) + ","
            nkey += 1
        if nkey == 1:
            ret += "},"
        else:
            ret += "<br>" + preSpace + "},"
    return ret[0:-1]
