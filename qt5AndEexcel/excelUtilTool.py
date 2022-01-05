
#!/usr/bin/env python3
# coding=utf-8
__author__ = 'Jianggb'
import sys,os,xlrd,xlwt,traceback
from time import gmtime
from xlrd import book, sheet, xldate_as_tuple
from datetime import datetime
from publicTool import *
from PublicLogTool import logger
from httpClient import httpClient
class myExcel:
    "excel解析类"
    def __init__(self, path):
        "初始化"
        self.path:str = path
        self.qsfieldName = ["id", "mid"] #qslist sheet页解析表头
        self.mapfieldName = ["类型", "名称", "结构", "空间"] #map sheet页解析表头
        self.respfieldName = ["反应模式", "宏观执行", "触发", "记忆支持", "记忆反对", "执行", "执行顺序", "重要度"] #反应模式 sheet页解析表头
        self.generalizefieldName = ["标准语义", "泛化语义", "关键词"] #反应模式 sheet页解析表头
        self.setFunc = self.UpText
        self.reset()
        self.baseactlist = [] #基础行为列表
        self.map2Struct:dict[str, dict] = {} #map sheet页mid结构列表
        self.mapSpaceDic:dict[str, dict] = {} #map sheet页mid空间列表
        self.qsBindlist = [] #id?约束
        self.rfBindlist = [] #id*约束
        self.respList:list[dict[str, str]] = [] #反应模式 sheet页解析后列表
        self.generalList:list[dict[str, str]] = [] #泛化 sheet页解析后列表
        self.knowledgeList:list[dict[str, str]] = [] #知识 sheet页解析后列表
        self.statList:list[dict[str, str]] = [] #统计 sheet页解析后列表
        self.httpClient = httpClient()
        self.clientid = None
        self.allbase = []

    def parseRet(self, retdic):
        "解析返回结果"
        try:
            if retdic["returncode"] == '0':
                ret = retdic["msg"]
                return ret
            else:
                return retdic
        except Exception as e:
            traceback.print_exc()
            return retdic

    def reset(self):
        "重置"
        self.mapList:list[dict[str, str]] = []  #map sheet页解析后列表
        self.macList = [] #宏观行为列表
        self.qslist = {} #id?列表
        self.rflist = {} #id*列表
        self.workbook = None
        self.respList:list[dict[str, str]] = [] #反应模式 sheet页解析后列表
        self.map2Struct:dict[str, dict] = {} #map sheet页mid结构列表
        self.generalList:dict[dict[str,str]] = [] #泛化 sheet页解析后列表
        self.knowledgeList: list[dict[str, str]] = []  # 知识 sheet页解析后列表
        self.statList:list[dict[str, str]] = [] #统计 sheet页解析后列表
        self.qsBindlist = [] #id?约束
        self.rfBindlist = [] #id*约束
        self.allbase = []

    def setPath(self, path, setFunc):
        "设置解析文件"
        self.path:str = path
        self.setFunc = setFunc

    def UpText(self, content): 
        logger.info(content)

    def analysisExlFile(self, mode=0):
        "解析文件内容"
        self.reset()
        fileName = self.path
        try:
            if fileName:
                if os.path.exists(fileName):
                    extname = os.path.splitext(fileName)[-1].lower()
                    if extname == '.xls' or extname == '.xlsx':
                        self.setFunc(蓝("解析文件:" + fileName))
                        # 确认是xls结尾还是xlsx结尾
                        if extname == '.xlsx':
                            self.workbook = xlrd.open_workbook(fileName)
                        else:
                            self.workbook = xlrd.open_workbook(fileName, formatting_info=True)
                        if mode == 0:
                            if "文本泛化" in self.workbook._sheet_names:
                                sheet = self.workbook.sheet_by_name("文本泛化")
                                self.analysisGeneralizeSheet(sheet)
                                self.setFunc(蓝("解析泛化文件完成"))
                                self.sendStructData()
                        elif mode == 1:
                            if "qslist" in self.workbook._sheet_names:
                                # id?映射
                                sheet = self.workbook.sheet_by_name("qslist")
                                self.analysisQslistSheet(sheet)
                            if "rflist" in self.workbook._sheet_names:
                                # id*映射
                                sheet = self.workbook.sheet_by_name("rflist")
                                self.analysisRflistSheet(sheet)
                            if "map" not in self.workbook._sheet_names or \
                                    "反应模式" not in self.workbook._sheet_names:
                                self.setFunc(fileName + 红("map、反应模式 sheet页不存在"))
                                return
                            sheet = self.workbook.sheet_by_name("map")
                            self.analysisMapSheet(sheet)
                            self.buildMstruct()
                            sheet = self.workbook.sheet_by_name("反应模式")
                            self.analysisRespSheet(sheet)
                            ret = self.sendStructData()
                            self.setFunc(buildColorTxt(ret, 0))
                            self.setFunc(蓝("解析文件完成"))
                        elif mode == 2:
                            if "知识" in self.workbook._sheet_names:
                                sheet = self.workbook.sheet_by_name("知识")
                                self.analysisKnowsSheet(sheet)
                                # 检查导入结构
                                if "rflist" in self.workbook._sheet_names:
                                    # id*映射
                                    sheet = self.workbook.sheet_by_name("rflist")
                                    self.analysisRflistSheet(sheet)
                                if self.buildTargetListSpaceDict(self.knowledgeList, self.mapfieldName):
                                    self.setFunc(蓝("解析文件完成"))
                                    ret = self.sendStructData()
                                    self.setFunc(buildColorTxt(ret, 0))
                            else:
                                self.setFunc(红("没检测到“知识“sheet"))
                        elif mode == 3:
                            if "统计" in self.workbook._sheet_names:
                                sheet = self.workbook.sheet_by_name("统计")
                                self.analysisStatSheet(sheet) # self.statList update
                                if self.buildTargetListSpaceDict(self.statList, self.mapfieldName):
                                    self.setFunc(蓝("解析文件完成"))
                                    ret = self.sendStructData()
                                    self.setFunc(buildColorTxt(ret, 0))
                            else:
                                self.setFunc(红("没检测到统计sheet"))
                        else:
                            self.setFunc(fileName + 红("map、反应模式 sheet页不存在"))

                    else:
                        self.setFunc(fileName + 红("不是excel文件,不处理"))
                else:
                    self.setFunc(红(fileName + "不存在"))
        except Exception:
            self.setFunc(红("输入模版格式有问题或小工具解析问题"))
            self.setFunc(红(traceback.format_exc()))

    def analysisKnowsSheet(self, sheet):
        "解析知识 sheet"
        sheetlist = self.analysisSheet2List(sheet, self.mapfieldName)
        self.knowledgeList += sheetlist
        logger.info(f"self.knowledgeList:{self.knowledgeList}")

    def analysisStatSheet(self, sheet):
        "解析统计sheet"
        sheetlist = self.analysisSheet2List(sheet, self.mapfieldName)
        self.statList += sheetlist
        logger.info(f"self.statList: {self.statList}")

    def analysisGeneralizeSheet(self, sheet):
        "解析泛化 sheet"
        sheetlist = self.analysisSheet2List(sheet, self.generalizefieldName)
        self.generalList += sheetlist
        logger.info(f"self.generalizeList:{self.generalList}")

    def sendStructData(self):
        "发送解析好的excel数据"
        path = "analysisExlFile"
        data = {"clientid":str(self.clientid), "map2Struct":str(self.map2Struct), 
                "qslist":str(self.qslist), "rflist":str(self.rflist), 
                "qsBindlist":str(self.qsBindlist), "rfBindlist":str(self.rfBindlist),
                "respList":str(self.respList), "allbase":str(self.allbase),
                "mapSpaceDic":str(self.mapSpaceDic),"generalList": str(self.generalList),
                "knowledgeList": str(self.knowledgeList), "statList":str (self.statList)}
        retdic = self.httpClient.post(path, data)
        return self.parseRet(retdic)

    def rewrite2sheet(self):
        "把?id *id重新写入sheet页"
        workbook = xlwt.Workbook(encoding='gbk')
        sheet:xlwt.Worksheet = workbook.add_sheet("qslist")
        for i in range(len(self.qsfieldName)):
            sheet.write(0, i, self.qsfieldName[i])
        r = 1
        for id in self.qslist:
            sheet.write(r, 0, id)
            sheet.write(r, 1, self.qslist[id])
            r += 1

        sheet:xlwt.Worksheet = workbook.add_sheet("rflist")
        for i in range(len(self.qsfieldName)):
            sheet.write(0, i, self.qsfieldName[i])
        r = 1
        for id in self.rflist:
            sheet.write(r, 0, id)
            sheet.write(r, 1, self.rflist[id])
            r += 1
        extpos = self.path.rfind(".")
        name = f"{self.path[0:extpos]}_qslist{self.path[extpos:]}"
        workbook.save(name)

    def pickBracket(self, instr:str):
        "解析出文本中{}中内容"
        retList = []
        bpos = 0
        epos = 0
        while epos < len(instr):
            bpos = instr.find('{',epos)
            if bpos == -1:
                break
            epos = instr.find('}',bpos)
            if epos == -1:
                break
            tmpid = instr[bpos+1: epos]
            retList.append(tmpid)

        return retList

    def analysisMapSheet(self, sheet:sheet.Sheet):
        "解析map sheet"
        sheetlist = self.analysisSheet2List(sheet, self.mapfieldName)
        self.mapList += sheetlist

    def analysisQslistSheet(self, sheet:sheet.Sheet):
        "解析?id对应关系"
        sheetlist = self.analysisSheet2List(sheet, self.qsfieldName)
        for qs in sheetlist:
            qid = qs["id"]
            mid:str = qs["mid"]
            if qid not in self.qslist:
                self.qslist[qid] = mid.strip()

    def analysisRflistSheet(self, sheet:sheet.Sheet):
        "解析id*对应关系"
        sheetlist = self.analysisSheet2List(sheet, self.qsfieldName)
        for qs in sheetlist:
            qid = qs["id"]
            mid:str = qs["mid"]
            if qid not in self.rflist:
                self.rflist[qid] = mid.strip()

    def cell2Str(self, cell:sheet.Cell):
        "单元格内容转字符串"
        ctype = cell.ctype
        cellval = cell.value
        if ctype == 2 and cellval % 1 == 0.0:  # ctype为2且为浮点
            cellval = int(cellval)  # 浮点转成整型
            cellval = str(cellval)  # 转成整型后再转成字符串，如果想要整型就去掉该行
        elif ctype == 3:#时间
            date = datetime(*xldate_as_tuple(cellval, 0))
            cellval = date.strftime('%Y/%m/%d %H:%M:%S')
        elif ctype == 4:#bool
            cellval = True if cellval == 1 else False
        return str(cellval).strip()

    def analysisSheet2List(self, sheet:sheet.Sheet, fieldlist:list):
        "解析sheet"
        if sheet.nrows == 0:
            return []
        mergeDic,lastrow = self.mergedCell(sheet)
        firstrow = sheet.row_values(lastrow)
        head = {}
        for i in range(len(firstrow)):
            cell = sheet.cell(lastrow, i)
            if (lastrow, i) in mergeDic:
                cell = sheet.cell(*mergeDic[(lastrow, i)])
            val = self.cell2Str(cell)
            if val in fieldlist:
                head[val] = i

        #logger.info(head)

        sheetList = []
        for i in range(lastrow+1, sheet.nrows):
            rowdic = self.line2Dic(sheet, i, head)
            if rowdic:
                sheetList.append(rowdic)

        #logger.info(sheetList)
        return sheetList

    def line2Dic(self, sheet:sheet.Sheet, row, headMap:dict):
        "行转字典"
        retdic = {}
        empty = True
        for key in headMap:
            if headMap[key] == None or headMap[key] < 0:
                continue
            sval = self.cell2Str(sheet.cell(row, headMap[key]))
            if sval and empty:
                empty = False
            retdic[key] = self.transF2H(sval)
        if empty:
            return None
        else:
            return retdic

    def analysisRespSheet(self, sheet:sheet.Sheet):
        "解析反应模式 sheet"
        sheetlist = self.analysisSheet2List(sheet, self.respfieldName)
        self.respList += sheetlist
        logger.info(f"self.respList:{self.respList}")
        
    def mergedCell(self, sheet:sheet.Sheet):
        "合并的单元格获取"
        retdic = {}
        lastrow = 0
        for i in sheet.merged_cells:
            for r in range(i[0], i[1]):
                for c in range(i[2], i[3]):
                    if r > lastrow and c == 0:
                        lastrow = r
                    retdic[(r,c)] =  (i[0], i[2])
        return retdic, lastrow

    def transF2H(self, sline):
        "全角符号转半角"
        rstring = ""
        for uchar in sline:
            inside_code=ord(uchar)
            if inside_code == 12288:                              #全角空格直接转换            
                inside_code = 32 
            elif (inside_code >= 65281 and inside_code <= 65374): #全角字符（除空格）根据关系转化
                inside_code -= 65248
            elif 8221 == inside_code or 8220 == inside_code: #双引号“”
                inside_code = 34

            rstring += chr(inside_code)
        return rstring

    def buildTargetListSpaceDict(self, target_list, fields):
        for line in target_list:
            for item in fields:
                if item not in line:
                    self.setFunc(红(f"导入文件位格不对,缺少需要{item}"))
                    return False
            self.mapSpaceDic[line["名称"]] = line["空间"]
            self.analysisLine(line["名称"], line["结构"])

        logger.info(f"self.mapSpaceDic:{self.mapSpaceDic}")
        logger.info(f"self.map2Struct:{self.map2Struct}")
        logger.info(f"self.rfBindlist:{self.rfBindlist}")
        return True

    def buildMstruct(self):
        "处理mapList中的结构列到mstruct Map"
        for line in self.mapList:
            if "类型" not in line or "名称" not in line or "结构" not in line:
                continue
            type = line["类型"]
            name = line["名称"]
            space = line["空间"] if "空间" in line else None
            if space:
                self.mapSpaceDic[name] = space
            self.analysisLine(name, line["结构"])
            if type == "宏观执行":
                self.macList.append(name)
            elif type == "基础执行":
                if name not in self.map2Struct:
                    self.setFunc(红(f"[{name}]么有定义"))
                    continue
                dic = self.map2Struct[name]
                act = dic["执行"] if "执行" in dic else None
                if act and act not in self.allbase:
                    self.allbase.append(act)
                elif not act:
                    self.setFunc(红(f"[{name}]么有执行"))
                    continue

        logger.info(f"self.mapSpaceDic:{self.mapSpaceDic}")
        logger.info(f"self.map2Struct:{self.map2Struct}")
        logger.info(f"self.qsBindlist:{self.qsBindlist}")
        logger.info(f"self.rfBindlist:{self.rfBindlist}")

    def analysisLine(self, name, sline):
        "解析map sheet页中结构列"
        if not sline or sline[0] != "(":
            logger.error(f"[{sline}]第一个字符不是(")
            return
        curlyMap = self.curlyPos(sline)
        if curlyMap and 0 in curlyMap:
            endpos = curlyMap[0]
            retMap = self.split2Dic(name, sline[1:endpos])
            if retMap:
                self.map2Struct[name] = retMap
            #解析?id约束
            for beginpos in curlyMap:
                if beginpos > endpos:
                    endpos = curlyMap[beginpos]
                    retMap = self.split2Dic(name, sline[beginpos+1:endpos])
                    hasQs = False
                    hasRf = False
                    for val in retMap.values():
                        if val[0] == "?":
                            hasQs = True
                            break
                        elif val[0] == "*":
                            hasRf = True
                            break
                    if hasQs:
                        self.qsBindlist.append(retMap)
                    if hasRf:
                        self.rfBindlist.append(retMap)

    def split2Dic(self, name, strin:str, splitor1=",", splitor2="="):
        "将strin按照splitor1 splitor2分割成字典"
        curlyMap = self.curlyPos(strin)
        retMap = {}
        pos = 0
        while pos < len(strin):
            s2pos = strin.find(splitor2, pos)
            if s2pos == -1:
                break
            key = strin[pos: s2pos]
            val = None
            if strin[s2pos+1] == "(":
                "嵌套子结构,约定以()括起"
                val = f"{name}_{key}"
                sretMap = self.split2Dic(val, strin[s2pos+2 : curlyMap[s2pos+1]])
                if sretMap:
                    self.map2Struct[val] = sretMap
                pos = curlyMap[s2pos+1] + 2
            elif strin[s2pos+1] == "\"":
                "以\"\"括起的字符"
                nextrPos = strin.find("\"",s2pos+2)
                if nextrPos == -1:
                    s1pos = strin.find(splitor1, s2pos+2)
                    if s1pos == -1:
                        val = strin[s2pos+2 : ]
                        pos = len(strin) + 1
                    else:
                        val = strin[s2pos+2 : s1pos]
                        pos = s1pos + 1
                else:
                    while strin[nextrPos-1] == "\\":
                        prePos = nextrPos
                        nextrPos = strin.find("\"",nextrPos+1)
                        if nextrPos == -1:
                            nextrPos = prePos
                            break
                    val = strin[s2pos+1 : nextrPos+1]
                    s1pos = strin.find(splitor1, nextrPos+1)
                    if s1pos == -1:
                        pos = len(strin) + 1
                    else:
                        pos = s1pos + 1
            else:
                s1pos = strin.find(splitor1, s2pos)
                if s1pos == -1:
                    val = strin[s2pos+1 : ]
                    pos = len(strin) + 1
                else:
                    val = strin[s2pos+1 : s1pos]
                    pos = s1pos + 1
            if val[0] == "?" and val not in self.qslist:
                "添加id?列表"
                self.qslist[val] = None
            if val[0] == "*" and val not in self.rflist:
                "添加id*列表"
                self.rflist[val] = None
            key = key.rstrip().lstrip()
            val = val.rstrip().lstrip()
            retMap[key] = val
        return retMap

    def curlyPos(self, strin:str):
        "解析左右括号的位置"
        leftcurlyPosList = []
        curlyMap = {}
        isInMark = False
        for i in range(len(strin)):
            
            if strin[i] == "\"" and i > 1 and strin[i] != "\\":
                if not isInMark:
                    isInMark = True
                else:
                    isInMark = False
            if isInMark:
                "在""内的()不计入"
                continue
            if strin[i] == "(":
                leftcurlyPosList.append(i)
            elif strin[i] == ")":
                if not leftcurlyPosList:
                    self.setFunc(红(f"[{strin}]括号不配对"))
                    return {}
                curlyMap[leftcurlyPosList.pop()] = i
        if leftcurlyPosList:
            self.setFunc(红(f"[{strin}]括号不配对"))
            return {}
        return curlyMap

    def queryRespByMacid(self, mid):
        "通过宏观行为查询反应模式"
        path = "queryRespByMacid"
        params = {"mid":str(mid)}
        retdic = self.httpClient.post(path, params)
        return self.parseRet(retdic)

    def addStat(self):
        "添加统计"
        path = "addStat"
        retdic = self.httpClient.post(path, {"clientid": str(self.clientid)})
        return self.parseRet(retdic)

    def rmStat(self):
        "删除统计"
        path = "rmStat"
        retdic = self.httpClient.post(path, {"clientid": str(self.clientid)})
        return self.parseRet(retdic)

    def addgeneralize(self):
        "添加泛化"
        path = "addgeneralize"
        retdic = self.httpClient.post(path, {"clientid": str(self.clientid)})
        return self.parseRet(retdic)

    def rmgeneralize(self):
        "删除泛化"
        path = "rmgeneralize"
        retdic = self.httpClient.post(path, {"clientid": str(self.clientid)})
        return self.parseRet(retdic)

    def addResp(self):
        "添加反应模式"
        path = "addResp"
        retdic = self.httpClient.post(path, {"clientid":str(self.clientid)})
        return self.parseRet(retdic)

    def removeAddid(self):
        "删除所有已生成id"
        path = "removeAddid"
        retdic = self.httpClient.post(path, {"clientid":str(self.clientid)})
        return self.parseRet(retdic)

    def getAllResp(self):
        path = "getAllResp"
        retdic = self.httpClient.post(path, {"clientid": str(self.clientid)})
        return self.parseRet(retdic)

    def getAllAct(self, mid, uid):
        path = "getAllAct"
        retdic = self.httpClient.post(path, {"mid": mid, "uid":uid})
        return self.parseRet(retdic)

    def delCurByIds(self, ids):
        path = "delCurByIds"
        retdic = self.httpClient.post(path, {"ids": ids})
        return self.parseRet(retdic)

    def delCurByDomain(self, domains):
        path = "delCurByDomain"
        retdic = self.httpClient.post(path, {"domains": domains})
        return self.parseRet(retdic)
        
    def connect(self, ipPort, version):
        path = "connect"
        self.httpClient.setIpPort(ipPort)
        retdic = self.httpClient.post(path, {"clientid":str(self.clientid), "version": version})
        try:
            if "需要版本" in retdic["msg"]:
                retdic["当前版本"] = version
            self.clientid = retdic["msg"]["clientid"]
        except Exception as e:
            logger.info(str(e))
        return retdic

    def resvMsg(self):
        path = "loopGetResp"
        retdic = self.httpClient.post(path, {"clientid":str(self.clientid)})
        return self.parseRet(retdic)

    def resvLog(self):
        path = "loopGetLog"
        retdic = self.httpClient.post(path, {"clientid":str(self.clientid)})
        return self.parseRet(retdic)

    def sendMsg(self, msg):
        path = "sendMsg"
        sendmsg = {"clientid":str(self.clientid), "msg":msg}
        retdic = self.httpClient.post(path, sendmsg)
        return self.parseRet(retdic)

    def closeWind(self):
        path = "closeWind"
        sendmsg = {"clientid":str(self.clientid)}
        retdic = self.httpClient.post(path, sendmsg)
        return self.parseRet(retdic)

    def addKnow(self, ivs, spaceid):
        "增加知识"
        path = "addKnow"
        retdic = self.httpClient.post(path, {"ivs":ivs, "spaceid":spaceid, "clientid":str(self.clientid)})
        return self.parseRet(retdic)

    def restartTest(self):
        "重新开始测试"
        path = "restartTest"
        retdic = self.httpClient.post(path, {"clientid":str(self.clientid)})
        return self.parseRet(retdic)

if __name__ == '__main__':
    myexl = myExcel("/home/jgb/MTS/respClient/0825_resp.xlsx")
    strin = "主语=自身，执行=生成约束，对象=？25，空间=“具体对象”，内容=（主语=？25，属类=文章）"
    strin = myexl.transF2H(strin)
    ret = myexl.split2Dic("aa",strin )
    # ret = myexl.getAllBas()
    logger.info(ret)
    # # ret = myexl.transF2H("（主语=自身，执行=发送，内容=（（主语=自身，执行=祈使检测，执行状态=完成））")
    # myexl.analysisLine("test",ret)
