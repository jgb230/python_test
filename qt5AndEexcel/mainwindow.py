
#!/usr/bin/env python3
# coding=utf-8
__author__ = 'Jianggb'
import sys,os

from PyQt5 import QtWidgets,QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from publicTool import *
from PublicLogTool import logger
from excelUtilTool import myExcel
from knowQueryTool import knowquery
import time, traceback

class myWind(QMainWindow):
    def __init__(self):
        super(myWind, self).__init__()
        self.initUI()
        self.exUtil:myExcel = myExcel("")
        self.kq = knowquery(self.exUtil.httpClient)
        self.clientid = ""
        self.resvMsgList = [] #接收到的消息列表
        self.resvlogList = [] #日志列表
        self.sendMsgList = [] #发送的消息列表
        self.isStartResv = False #获取消息线程是否开启
        self.ipPortStr = ""
        self.version = "1.0.12.25"

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:

        return super().closeEvent(a0)

    def setResptxt(self, txt):
        "设置反应模式富文本内容"
        self.setEdittxt(self.addresplabal, txt)

    def setgeneralizetxt(self, txt):
        "设置反应模式富文本内容"
        self.setEdittxt(self.addgeneralizelabel, txt)

    def setaKnowtxt(self, txt):
        "设置a知识富文本内容"
        self.setEdittxt(self.aKonwlabal, txt)

    def setKnowtxt(self, edit:QTextEdit, txt):
        "设置知识富文本内容"
        self.setEdittxt(edit, txt)

    def setStattxt(self, txt):
        self.setEdittxt(self.Statlabel, txt)

    def setEdittxt(self, edit:QTextEdit, txt):
        "设置富文本内容"
        edit.append(txt)
        edit.append(蓝("="*40))
        # 设置滚动条到最低部
        cursor = edit.textCursor()
        pos = len(edit.toPlainText())
        cursor.setPosition(pos-1)
        edit.ensureCursorVisible()
        edit.setTextCursor(cursor)

    def getAddResp(self):
        "添加反应模式页面"
        groupBox = QGroupBox("添加反应模式")
        hlayout=QGridLayout()
        but = QPushButton("选择文件")
        but.clicked[bool].connect(self.openFile)
        hlayout.addWidget(but, 0, 0)
        but = QPushButton("删除")
        but.setStyleSheet("QPushButton{font-famili:'宋体';color:rgb(255,0,0)}")
        but.clicked[bool].connect(self.removeAddid)
        hlayout.addWidget(but, 0, 1)
        but = QPushButton("添加")
        but.clicked[bool].connect(self.addResp)
        hlayout.addWidget(but, 0, 2)
        self.addresplabal = QTextEdit()
        hlayout.addWidget(self.addresplabal, 1, 0, 3, 3)
        groupBox.setLayout(hlayout)
        return groupBox

    def getGetAllAct(self):
        "查询所有反应模式页面"
        groupBox = QGroupBox("查询所有反应模式")
        hlayout = QGridLayout()
        actidLabel = QLineEdit()
        hlayout.addWidget(actidLabel, 0, 1)
        uidLabel = QLineEdit()
        hlayout.addWidget(uidLabel, 1, 1)
        but = QPushButton("查询")
        but.clicked[bool].connect(lambda: self.getAllAct(actidLabel.text(), uidLabel.text()))
        hlayout.addWidget(but, 0, 2)
        labal = QLabel("Mid触发确认：")
        hlayout.addWidget(labal, 0, 0)
        labal = QLabel("输入Uid：")
        hlayout.addWidget(labal, 1, 0)

        but = QPushButton("所有激活触发")
        but.clicked[bool].connect(lambda: self.getAllAct('', ''))
        hlayout.addWidget(but, 1, 2)

        self.actlabel = QTextEdit()
        hlayout.addWidget(self.actlabel, 2, 0, 2, 3)
        groupBox.setLayout(hlayout)
        return groupBox

    def getAddStat(self):
        "添加统计页面"
        groupBox = QGroupBox("更新统计")
        statayout = QGridLayout()
        but = QPushButton("选择文件")
        but.clicked[bool].connect(self.openFile_Stat)
        statayout.addWidget(but, 0, 0)
        but = QPushButton("删除")
        but.setStyleSheet("QPushButton{font-famili:'宋体';color:rgb(255,0,0)}")
        but.clicked[bool].connect(self.rmStat)
        statayout.addWidget(but, 0, 1)
        but = QPushButton("添加")
        but.clicked[bool].connect(self.addStat)
        statayout.addWidget(but, 0, 2)
        self.Statlabel = QTextEdit()
        statayout.addWidget(self.Statlabel, 1, 0, 3, 3)
        groupBox.setLayout(statayout)
        return groupBox

    def getAddgeneralize(self):
        "添加泛化模式页面"
        groupBox = QGroupBox("更新泛化")
        hlayout=QGridLayout()
        but = QPushButton("选择文件")
        but.clicked[bool].connect(self.openFile_fh)
        hlayout.addWidget(but, 0, 0)
        but = QPushButton("删除")
        but.setStyleSheet("QPushButton{font-famili:'宋体';color:rgb(255,0,0)}")
        but.clicked[bool].connect(self.rmgeneralize)
        hlayout.addWidget(but, 0, 1)
        but = QPushButton("添加")
        but.clicked[bool].connect(self.addgeneralize)
        hlayout.addWidget(but, 0, 2)
        self.addgeneralizelabel = QTextEdit()
        hlayout.addWidget(self.addgeneralizelabel, 1, 0, 3, 3)
        groupBox.setLayout(hlayout)
        return groupBox

    def getQueryResp(self):
        "查询反应模式页面"
        groupBox = QGroupBox("查询反应模式")
        hlayout=QGridLayout()
        qresplabal = QLineEdit()
        hlayout.addWidget(qresplabal, 0, 1)
        but = QPushButton("查询")
        but.clicked[bool].connect(lambda:self.queryResp(qresplabal.text()))
        hlayout.addWidget(but, 0, 2)
        labal = QLabel("输入宏观行为")
        hlayout.addWidget(labal, 0, 0)

        but = QPushButton("所有反应模式")
        but.clicked[bool].connect(lambda: self.getAllResp())
        hlayout.addWidget(but, 0, 3)

        # but = QPushButton("查询已挂起的触发")
        # but.clicked[bool].connect(lambda: self.getAllAct(qresplabal.text()))
        # hlayout.addWidget(but, 1, 1)

        self.qresplabal = QTextEdit()
        hlayout.addWidget(self.qresplabal, 1, 0, 2, 4)
        groupBox.setLayout(hlayout)
        return groupBox

    def trimTxt(self, mid:str):
        "trim引号和空格"
        mid = mid.strip("' \"")
        return mid

    def queryResp(self, mid):
        "查询mid宏观行为对应的反应模式结构"
        dic = self.exUtil.queryRespByMacid(self.trimTxt(mid))
        self.setKnowtxt(self.qresplabal, buildColorTxt(dic, 0))

    def getAllResp(self):
        "查询所有导入反应模式"
        dic = self.exUtil.getAllResp()
        self.setKnowtxt(self.qresplabal, buildColorTxt(dic, 0))

    def getAllAct(self, mid, uid):
        "查询所有激活触发"
        if len(uid) == 0:
            uid = "0"
        dic = self.exUtil.getAllAct(self.trimTxt(mid), uid)
        self.setKnowtxt(self.actlabel, buildColorTxt(dic, 0))

    def addResp(self):
        "添加反应模式"
        ret = self.exUtil.addResp()
        self.setKnowtxt(self.addresplabal, buildColorTxt(ret))

    def rmStat(self):
        "删除反应模式"
        reply = QMessageBox.question(self, "是否删除", "确定要删除吗", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        ret = self.exUtil.rmStat()
        self.setStattxt(buildColorTxt(ret))

    def addStat(self):
        "添加反应模式"
        ret = self.exUtil.addStat()
        self.setStattxt(buildColorTxt(ret))

    def addgeneralize(self):
        "添加泛化"
        ret = self.exUtil.addgeneralize()
        self.setKnowtxt(self.addgeneralizelabel, buildColorTxt(ret))

    def rmgeneralize(self):
        "删除泛化"
        reply = QMessageBox.question(self, "是否删除", "确定要删除吗", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        ret = self.exUtil.rmgeneralize()
        self.setKnowtxt(self.addgeneralizelabel, 红(str(ret)))

    def removeAddid(self):
        "删除所有id"
        # _thread.start_new_thread(self.exUtil.removeAddid, ())
        reply = QMessageBox.question(self, "是否删除", "确定要删除吗", QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return 
        ret = self.exUtil.removeAddid()
        self.setKnowtxt(self.addresplabal, 红(str(ret)))

    def openFile(self):
        "打开选择文件框"
        fileName, fileType = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", os.getcwd())
        self.setKnowtxt(self.addresplabal, 蓝(f"选择文件:{fileName}"))
        self.exUtil.setPath(fileName, self.setResptxt)
        ret = self.exUtil.analysisExlFile(mode=1)

    def openFile_fh(self):
        "打开选择文件框"
        fileName, fileType = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", os.getcwd())
        self.exUtil.setPath(fileName, self.setgeneralizetxt)
        self.setKnowtxt(self.addgeneralizelabel, 蓝(f"选择文件:{fileName}"))
        ret = self.exUtil.analysisExlFile(mode=0)

    def openFile_know(self):
        "打开选择文件框"
        fileName, fileType = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", os.getcwd())
        self.exUtil.setPath(fileName, self.setaKnowtxt)
        self.setKnowtxt(self.aKonwlabal, 蓝(f"选择文件:{fileName}"))
        ret = self.exUtil.analysisExlFile(mode=2)

    def openFile_Stat(self):
        "打开选择文件框"
        fileName, fileType = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", os.getcwd())
        self.exUtil.setPath(fileName, self.setStattxt)
        self.setStattxt(蓝(f"选择文件:{fileName}"))
        ret = self.exUtil.analysisExlFile(mode=3)

    def getCuriosity(self):
        "好奇心页面"
        groupBox = QGroupBox('好奇心', self)
        grid = QGridLayout(groupBox)

        but = QPushButton("查询好奇心")
        but.clicked[bool].connect(lambda: self.clayoutSet(0))
        grid.addWidget(but, 0, 0)
        but = QPushButton("删除好奇心")
        but.clicked[bool].connect(lambda: self.clayoutSet(1))
        grid.addWidget(but, 0, 1)
        but = QPushButton("删除领域好奇")
        but.clicked[bool].connect(lambda: self.clayoutSet(2))
        grid.addWidget(but, 0, 2)

        gwg = QWidget(self)
        self.clayout = QStackedLayout(gwg)
        but = self.getCur()  # 查询好奇心
        self.clayout.addWidget(but)
        but = self.delCur()   # 删除好奇心
        self.clayout.addWidget(but)
        but = self.delCurRegion() # 删除领域好奇
        self.clayout.addWidget(but)

        grid.addWidget(gwg, 2, 0, 4, 3)
        groupBox.setLayout(grid)
        return groupBox

    def getStat(self):
        "统计页面"
        groupBox = QGroupBox('统计导入', self)
        grid = QGridLayout(groupBox)

        # but = QPushButton("查询统计")
        # but.clicked[bool].connect(lambda: self.statlayoutSet(0))
        # grid.addWidget(but, 0, 0)

        but = QPushButton("增加统计列表")
        but.clicked[bool].connect(lambda: self.statlayoutSet(0))
        grid.addWidget(but, 0, 0)

        gwg = QWidget(self)
        self.statlayout = QStackedLayout(gwg)

        # but = self.getGetStat()  # 增加统计
        # self.statlayout.addWidget(but)

        but = self.getAddStat()# 增加统计
        self.statlayout.addWidget(but)

        gwg.setLayout(self.statlayout)

        grid.addWidget(gwg, 1, 0)
        groupBox.setLayout(grid)
        return groupBox

    def getgeneralize(self):
        "泛化页面"
        groupBox = QGroupBox('泛化导入', self)
        grid = QGridLayout(groupBox)

        but = QPushButton("增加泛化列表")
        but.clicked[bool].connect(lambda: self.glayoutSet(0))
        grid.addWidget(but, 0, 0)

        gwg = QWidget(self)
        self.fhlayout = QStackedLayout(gwg)
        but = self.getAddgeneralize() # 增加泛化
        self.fhlayout.addWidget(but)

        gwg.setLayout(self.fhlayout)

        grid.addWidget(gwg, 1, 0)
        groupBox.setLayout(grid)
        return groupBox

    def getResp(self):
        "反应模式页面"
        groupBox = QGroupBox('反应模式', self)
        grid = QGridLayout(groupBox)

        but = QPushButton("添加反应模式")
        but.clicked[bool].connect(lambda:self.glayoutSet(0))
        grid.addWidget(but, 0, 0)
        but = QPushButton("查询反应模式")
        but.clicked[bool].connect(lambda:self.glayoutSet(1))
        grid.addWidget(but, 0, 1)
        but = QPushButton("删除反应模式")
        but.setStyleSheet("QPushButton{font-famili:'宋体';color:rgb(255,0,0)}")
        but.clicked[bool].connect(lambda:self.glayoutSet(2))
        grid.addWidget(but, 0, 2)
        # but = QPushButton("修改反应模式")
        # but.clicked[bool].connect(lambda:self.glayoutSet(3))
        # grid.addWidget(but, 0, 3)

        but = QPushButton("查询激活触发")
        but.clicked[bool].connect(lambda: self.glayoutSet(3))
        grid.addWidget(but, 0, 3)

        gwg=QWidget(self)
        self.glayout=QStackedLayout(gwg)
        but = self.getAddResp() #添加反应模式
        self.glayout.addWidget(but)
        but = self.getQueryResp() #查询反应模式
        self.glayout.addWidget(but)
        but = QPushButton("删除反应模式")
        self.glayout.addWidget(but)
        # but = QPushButton("修改反应模式")
        # self.glayout.addWidget(but)
        but = self.getGetAllAct() # 查询触发
        self.glayout.addWidget(but)
        gwg.setLayout(self.glayout)

        grid.addWidget(gwg, 2, 0, 5, 4)
        groupBox.setLayout(grid)
        return groupBox

    def statlayoutSet(self, idx):
        print(f"{idx} {self.statlayout.count()}")
        if idx < self.statlayout.count():
            self.statlayout.setCurrentIndex(idx)
        else:
            self.statlayout.setCurrentIndex(1)

    def glayoutSet(self, idx):
        print(f"{idx} {self.glayout.count()}")
        if idx < self.glayout.count():
            self.glayout.setCurrentIndex(idx)
        else:
            self.glayout.setCurrentIndex(0)

    def clayoutSet(self, idx):
        print(f"{idx} {self.clayout.count()}")
        if idx < self.clayout.count():
            self.clayout.setCurrentIndex(idx)
        else:
            self.clayout.setCurrentIndex(0)

    def klayoutSet(self, idx):
        print(f"{idx} {self.klayout.count()}")
        if idx < self.klayout.count():
            self.klayout.setCurrentIndex(idx)
        else:
            self.klayout.setCurrentIndex(0)

    def getKnow(self):
        groupBox = QGroupBox('知识', self)
        grid = QGridLayout(groupBox)

        but = QPushButton("叶子节点")
        but.clicked[bool].connect(lambda:self.klayoutSet(0))
        grid.addWidget(but, 0, 0)
        but = QPushButton("查询知识")
        but.clicked[bool].connect(lambda:self.klayoutSet(1))
        grid.addWidget(but, 0, 1)
        but = QPushButton("删除知识")
        but.setStyleSheet("QPushButton{font-famili:'宋体';color:rgb(255,0,0)}")
        but.clicked[bool].connect(lambda:self.klayoutSet(2))
        grid.addWidget(but, 0, 2)
        but = QPushButton("增加知识")
        but.clicked[bool].connect(lambda:self.klayoutSet(3))
        grid.addWidget(but, 0, 3)
        # but = QPushButton("好奇心")
        # but.clicked[bool].connect(lambda:self.klayoutSet(4))
        # grid.addWidget(but, 0, 4)

        gwg=QWidget(self)
        self.klayout=QStackedLayout(gwg)
        but = self.getQueryleafKnow() #叶子查询
        self.klayout.addWidget(but)
        but = self.getQueryKnow() #查询知识
        self.klayout.addWidget(but)
        but = self.getDelKnow() ##删除知识
        self.klayout.addWidget(but)
        but = self.getAddKnow() #增加知识
        self.klayout.addWidget(but)
        # but = self.getCur() #查询好奇心
        # self.klayout.addWidget(but)
        gwg.setLayout(self.klayout)

        grid.addWidget(gwg, 1, 0, 4, 4)
        groupBox.setLayout(grid)
        return groupBox

    def getQueryKnow(self):
        "查询知识页面"
        groupBox = QGroupBox("查询知识")
        hlayout=QGridLayout()
        knowlabal = QLineEdit()
        hlayout.addWidget(knowlabal, 0, 1)
        but = QPushButton("查询")
        but.clicked[bool].connect(lambda:self.queryKnow(knowlabal.text()))
        hlayout.addWidget(but, 0, 2)
        labal = QLabel("输入知识id")
        hlayout.addWidget(labal, 0, 0)
        self.qKonwlabal = QTextEdit()
        hlayout.addWidget(self.qKonwlabal, 1, 0, 2, 3)
        groupBox.setLayout(hlayout)
        return groupBox

    def getQueryleafKnow(self):
        "叶子查询知识页面"
        groupBox = QGroupBox("叶子节点")
        hlayout=QGridLayout()
        labal = QLabel("叶子节点id")
        hlayout.addWidget(labal, 0, 0)
        knowlabal = QLineEdit()
        hlayout.addWidget(knowlabal, 0, 1)
        labal = QLabel("空间")
        hlayout.addWidget(labal, 0, 2)
        comb = QComboBox()
        items = ['所有非疑问空间', '所有疑问空间']
        items += list(SpaceName._member_map_.keys())
        comb.addItems(items)
        hlayout.addWidget(comb, 0, 3)
        but = QPushButton("查询")
        but.clicked[bool].connect(lambda:self.queryleafKnow(knowlabal.text(), comb))
        hlayout.addWidget(but, 0, 4)
        self.lKonwlabal = QTextEdit()
        hlayout.addWidget(self.lKonwlabal, 1, 0, 2, 5)
        groupBox.setLayout(hlayout)
        return groupBox

    def getDelKnow(self):
        "删除知识页面"
        groupBox = QGroupBox("删除知识")
        groupBox.setStyleSheet("QGroupBox{font-famili:'宋体';color:rgb(255,0,0)}")
        hlayout=QGridLayout()
        knowlabal = QLineEdit()
        hlayout.addWidget(knowlabal, 0, 1)
        but = QPushButton("删除")
        but.setStyleSheet("QPushButton{font-famili:'宋体';color:rgb(255,0,0)}")
        but.clicked[bool].connect(lambda:self.delKnow(knowlabal.text()))
        hlayout.addWidget(but, 0, 2)
        labal = QLabel("输入知识id")
        hlayout.addWidget(labal, 0, 0)
        self.dKonwlabal = QTextEdit()
        hlayout.addWidget(self.dKonwlabal, 1, 0, 2, 3)
        groupBox.setLayout(hlayout)
        return groupBox

    def getAddKnow(self):
        "增加知识页面"
        groupBox = QGroupBox("增加知识")
        hlayout=QGridLayout()

        labal = QLabel("批量知识")
        hlayout.addWidget(labal, 0, 0)
        but = QPushButton("导入知识列表")
        but.clicked[bool].connect(self.openFile_know)
        hlayout.addWidget(but, 0, 1, 1, 3)
        # but = QPushButton("增加")
        # but.clicked[bool].connect(lambda: print(1))
        # hlayout.addWidget(but, 0, 4)

        labal = QLabel("知识内容")
        hlayout.addWidget(labal, 1, 0)
        knowlabal = QLineEdit()
        hlayout.addWidget(knowlabal, 1, 1)
        labal = QLabel("空间")
        hlayout.addWidget(labal, 1, 2)
        comb = QComboBox()
        items = list(SpaceName._member_map_.keys())
        comb.addItems(items)
        hlayout.addWidget(comb, 1, 3)
        but = QPushButton("增加")
        but.clicked[bool].connect(lambda:self.addKnow(knowlabal.text(), comb))
        hlayout.addWidget(but, 1, 4)
        self.aKonwlabal = QTextEdit()
        hlayout.addWidget(self.aKonwlabal, 2, 0, 2, 5)
        self.setKnowtxt(self.aKonwlabal, 紫('格式:{"key":"val"}'))
        groupBox.setLayout(hlayout)
        return groupBox

    def getCur(self):
        "好奇心页面"
        groupBox = QGroupBox("好奇心")
        hlayout=QGridLayout()
        labal = QLabel("uid")
        hlayout.addWidget(labal, 0, 0)
        knowlabal = QLineEdit()
        hlayout.addWidget(knowlabal, 0, 1)
        but = QPushButton("查询")
        but.clicked[bool].connect(lambda:self.queryCur(knowlabal.text()))
        hlayout.addWidget(but, 0, 2)
        self.curlabal0 = QTextEdit()
        hlayout.addWidget(self.curlabal0, 1, 0, 2, 3)
        groupBox.setLayout(hlayout)
        return groupBox

    def delCur(self):
        "删除好奇心页面"
        groupBox = QGroupBox("删除好奇心")
        hlayout = QGridLayout()
        labal = QLabel("好奇心id")
        hlayout.addWidget(labal, 0, 0)
        knowlabal = QLineEdit()
        hlayout.addWidget(knowlabal, 0, 1)
        but = QPushButton("删除")
        but.clicked[bool].connect(lambda: self.deleteCur(knowlabal.text()))
        hlayout.addWidget(but, 0, 2)
        self.curlabal1 = QTextEdit()
        hlayout.addWidget(self.curlabal1, 1, 0, 2, 3)
        groupBox.setLayout(hlayout)
        return groupBox

    def delCurRegion(self):
        "删除好奇领域页面"
        groupBox = QGroupBox("删除好奇心领域")
        hlayout = QGridLayout()
        labal = QLabel("领域")
        hlayout.addWidget(labal, 0, 0)
        knowlabal = QLineEdit()
        hlayout.addWidget(knowlabal, 0, 1)
        but = QPushButton("删除")
        but.clicked[bool].connect(lambda: self.deleteCurRegion(knowlabal.text()))
        hlayout.addWidget(but, 0, 2)
        self.curlabal2 = QTextEdit()
        hlayout.addWidget(self.curlabal2, 1, 0, 2, 3)
        groupBox.setLayout(hlayout)
        return groupBox

    def addKnow(self, txt:str, combo:QComboBox):
        "增加知识"
        spaceid = combo.currentText()
        ret = self.exUtil.addKnow(txt, spaceid)
        self.setKnowtxt(self.aKonwlabal, buildColorTxt(ret, 0))

    def queryleafKnow(self, mids:str, combo:QComboBox):
        "查询mid结构"
        ids = mids.split(",")
        spaceid = combo.currentText()
        ret = self.kq.queryByLeaf(ids, spaceid)
        self.setKnowtxt(self.lKonwlabal, buildColorTxt(ret, 0))

    def queryCur(self, uid:str):
        "查询好奇"
        uid = uid.strip(" '\"\\")
        ret = self.kq.queryCur(uid)
        self.setKnowtxt(self.curlabal0, buildColorTxt(ret, 0))

    def  deleteCur(self, cur_id_inp):
        raw_ids = cur_id_inp.strip(" []")  # 移除头尾空格或[]
        ids = []
        for i in raw_ids.split(','):
            ids.append(i)
        ret = self.exUtil.delCurByIds(ids)
        self.setKnowtxt(self.curlabal1, buildColorTxt(ret, 0))

    def deleteCurRegion(self, domains_inp):
        raw_domains = domains_inp.strip(" []")  # 移除头尾空格或[]
        domains = []
        for i in raw_domains.split(','):
            domains.append(i)
        ret = self.exUtil.delCurByDomain(domains)
        self.setKnowtxt(self.curlabal2, buildColorTxt(ret, 0))

    def queryKnow(self, mid:str):
        "查询mid结构"
        ids = mid.split(",")
        for sid in ids:
            ret = self.kq.queryByMid(self.trimTxt(sid))
            self.setKnowtxt(self.qKonwlabal, buildColorTxt(ret, 0))

    def delKnow(self, mid):
        "删除mid结构"
        reply = QMessageBox.question(self, "是否删除", "确定要删除吗", QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return 
        ids = mid.split(",")
        ret = self.kq.delMids(ids)
        self.setKnowtxt(self.dKonwlabal, buildColorTxt(ret, 0))

    def createButton(self, text):
        icon = QApplication.style().standardIcon(QStyle.SP_DesktopIcon)
        btn = QToolButton(self)
        btn.setText(text)
        btn.setIcon(icon)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        return btn

    def getConn(self):
        "连接页面"
        groupBox = QGroupBox("连接页面")
        hlayout=QGridLayout()
        self.clientidlabal = QLabel()
        hlayout.addWidget(self.clientidlabal, 1, 2)
        self.ipPort = QLineEdit()
        self.ipPort.setText("172.16.10.12:5566")
        hlayout.addWidget(self.ipPort, 0, 1, 1, 2)
        but = QPushButton("连接")
        but.clicked[bool].connect(lambda:self.connect(self.clientidlabal, self.ipPort.text()))
        hlayout.addWidget(but, 1, 0)
        labal = QLabel("客户端id")
        hlayout.addWidget(labal, 1, 1)
        labal = QLabel("ip:port")
        hlayout.addWidget(labal, 0, 0)

        # 快速链接按钮123、213、145·235
        labal = QLabel("快速链接:")
        hlayout.addWidget(labal, 2, 0)
        but = QPushButton("123")
        but.clicked[bool].connect(lambda: self.connect(self.clientidlabal, "172.16.0.123:5566"))
        hlayout.addWidget(but, 2, 1)
        but = QPushButton("213")
        but.clicked[bool].connect(lambda: self.connect(self.clientidlabal, "123.60.5.213:5566"))
        hlayout.addWidget(but, 2, 2)
        but = QPushButton("145")
        but.clicked[bool].connect(lambda: self.connect(self.clientidlabal, "124.71.192.145:5566"))
        hlayout.addWidget(but, 3, 1)
        but = QPushButton("235")
        but.clicked[bool].connect(lambda: self.connect(self.clientidlabal, "124.70.197.235:5566"))
        hlayout.addWidget(but, 3, 0)
        but = QPushButton("本地")
        but.clicked[bool].connect(lambda: self.connect(self.clientidlabal, "172.16.10.12:5566"))
        hlayout.addWidget(but, 3, 2)

        self.connedit = QTextEdit()
        hlayout.addWidget(self.connedit, 4, 0, 3, 3)
        groupBox.setLayout(hlayout)
        return groupBox

    def connect(self, qresplabal:QLabel, ip):
        "连接"
        ipPort = ip
        #ipPort = self.ipPort.text()
        self.ipPortStr = ipPort
        self.ipPort.setText(ipPort)
        ret = self.exUtil.connect(ipPort, self.version)
        try:
            self.clientid = ret["msg"]["clientid"]
            qresplabal.setText(str(self.clientid))
            self.setWindowTitle(f'一个工具 {self.ipPortStr} {self.clientid}')

            self.connedit.setText(buildColorTxt(ret, 0))
            if self.isStartResv == False:
                self.isStartResv = True
                self.msgT = msgThread(self.exUtil)#消息获取线程
                self.msgT.update.connect(self.resvMsgFunc)
                self.msgT.start()
                self.logT = logThread(self.exUtil)#日志获取线程
                self.logT.update.connect(self.resvLogFunc)
                self.logT.start()
        except Exception as e:
            traceback.print_exc()
            self.connedit.setText(buildColorTxt(ret, 0))

    def getTest(self):
        "反应模式测试页面"
        groupBox = QGroupBox("反应模式测试")
        hlayout=QGridLayout()
        self.ledit = QLineEdit()
        hlayout.addWidget(self.ledit, 3, 0, 1, 4)
        self.clientidlabalT = QLabel()
        hlayout.addWidget(self.clientidlabalT, 5, 1)
        but = QPushButton("发送")
        but.clicked[bool].connect(lambda:self.send(self.ledit.text()))
        hlayout.addWidget(but, 5, 3)
        but = QPushButton("重新开始")
        but.clicked[bool].connect(lambda:self.reset())
        hlayout.addWidget(but, 5, 2)
        labal = QLabel("客户端id")
        hlayout.addWidget(labal, 5, 0)
        self.msgTedit = QTextEdit()
        hlayout.addWidget(self.msgTedit, 0, 0, 3, 4)
        groupBox.setLayout(hlayout)
        return groupBox

    def reset(self):
        "清空记录"
        self.resvMsgList = []
        self.resvlogList = []
        self.sendMsgList = []
        self.msgTedit.clear()
        ret = self.exUtil.restartTest()
        text = 蓝(f"{ret}")
        self.setKnowtxt(self.msgTedit, text)

    def resvMsgFunc(self, msg):
        "获取消息的线程"
        if msg == "CLOSE":
            self.isStartResv = False
            text = 红(f"服务已关闭，请稍后再联系")
            self.setKnowtxt(self.msgTedit, text)
            self.setWindowTitle(f'一个工具 服务已关闭')
            return
        self.resvMsgList.append(msg)
        text = 青("AI:") + 红(f"{msg}")
        self.setKnowtxt(self.msgTedit, text)

    def resvLogFunc(self, msg):
        "获取日志的线程"
        if msg == "CLOSE":
            self.isStartResv = False
            text = 红(f"服务已关闭，请稍后再联系")
            self.setKnowtxt(self.connedit, text)
            self.setWindowTitle(f'一个工具 服务已关闭')
            return
        self.resvlogList.append(msg)
        text = 紫(f"{msg}")
        self.setKnowtxt(self.connedit, text)

    def send(self, text):
        "发送内容"
        tt = str(text).strip(" \n 　  \r")
        if len(tt) == 0:
            text = 青(f"AI:") + 红(f"发送消息为空")
            self.setKnowtxt(self.msgTedit, text)
            return 
        logger.info(f"发送:{text}")
        self.sendMsgList.append(text)
        ret = self.exUtil.sendMsg(text)
        text = 青(f"{self.clientid}:") + 蓝(f"{text}")
        self.setKnowtxt(self.msgTedit, text)
        text =  青(f"{self.clientid}:") + 蓝(f"{ret}")
        self.setKnowtxt(self.msgTedit, text)
        self.ledit.clear()

    def initUI(self):
        self.statusBar()
        plat = sys.platform

        mw = QWidget(self)
        self.mainLayout = QStackedLayout(mw)
        self.mainLayout.addWidget(self.getConn())
        self.mainLayout.addWidget(self.getResp())
        self.mainLayout.addWidget(self.getKnow())
        self.mainLayout.addWidget(self.getTest())
        self.mainLayout.addWidget(self.getgeneralize())
        self.mainLayout.addWidget(self.getCuriosity())
        self.mainLayout.addWidget(self.getStat())
        mw.setLayout(self.mainLayout)
        self.setCentralWidget(mw)

        self.toolBar = QToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)

        name = ""
        if plat == 'linux':
            name = '{: ^10}'.format("连接")
        else:
            name = '{: ^6}'.format("连接")
        btnColor = self.createButton(name)
        btnColor.clicked.connect(lambda: self.loadDir(0))
        self.toolBar.addWidget(btnColor)

        name = ""
        if plat == 'linux':
            name = '{: ^4}'.format("反应模式")
        else:
            name = '{: ^4}'.format("反应模式")
        btnColor = self.createButton(name)
        btnColor.clicked.connect(lambda: self.loadDir(1))
        self.toolBar.addWidget(btnColor)

        name = ""
        if plat == 'linux':
            name = '{: ^10}'.format("知识")
        else:
            name = '{: ^6}'.format("知识")
        btnColor = self.createButton(name)
        btnColor.clicked.connect(lambda: self.loadDir(2))
        self.toolBar.addWidget(btnColor)

        name = ""
        if plat == 'linux':
            name = '{: ^10}'.format("测试")
        else:
            name = '{: ^6}'.format("测试")
        btnColor = self.createButton(name)
        btnColor.clicked.connect(lambda: self.loadDir(3))
        self.toolBar.addWidget(btnColor)

        name = ""
        if plat == 'linux':
            name = '{: ^10}'.format("泛化")
        else:
            name = '{: ^6}'.format("泛化")
        btnColor = self.createButton(name)
        btnColor.clicked.connect(lambda: self.loadDir(4))
        self.toolBar.addWidget(btnColor)

        name = ""
        if plat == 'linux':
            name = '{: ^7}'.format("好奇心")
        else:
            name = '{: ^6}'.format("好奇心")
        btnColor = self.createButton(name)
        btnColor.clicked.connect(lambda: self.loadDir(5))
        self.toolBar.addWidget(btnColor)

        name = ""
        if plat == 'linux':
            name = '{: ^7}'.format("统计")
        else:
            name = '{: ^6}'.format("统计")
        btnColor = self.createButton(name)
        btnColor.clicked.connect(lambda: self.loadDir(6))
        self.toolBar.addWidget(btnColor)

        self.setGeometry(600,100,600,700)
        self.setWindowTitle('一个工具')

    def loadDir(self, idx):
        print(f"{idx} {self.mainLayout.count()}")
        self.ipPortStr = self.ipPort.text()
        self.setWindowTitle(f'一个工具 {self.ipPortStr} {self.clientid}')
        if idx < self.mainLayout.count():
            self.exUtil.httpClient.setIpPort(self.ipPortStr)
            self.mainLayout.setCurrentIndex(idx)
            if idx == 3:
                self.clientidlabalT.setText(str(self.clientid))
        else:
            self.mainLayout.setCurrentIndex(0)

class msgThread(QtCore.QThread):
    "消息获取线程"
    update = QtCore.pyqtSignal(str)
    def __init__(self, exUtil:myExcel):
        super().__init__()
        self.exUtil = exUtil
        self.timeInter = 100 #获取消息起始间隔ms

    def run(self):
        while True:
            try:
                msgs = self.exUtil.resvMsg()
                
                if isinstance(msgs, str):
                    if msgs.find("Connection refused"):
                        raise Exception("Connection refused")
                    msgs = [msgs]
                if isinstance(msgs, dict):
                    text = str(msgs)
                    if msgs.find("Connection refused"):
                        raise Exception("Connection refused")
                    msgs = [msgs]

                for msg in msgs:
                    self.update.emit(str(msg))
                time.sleep(float(self.timeInter/1000))
            except Exception as e:
                traceback.print_exc()
                self.update.emit("CLOSE")
                return

class logThread(QtCore.QThread):
    "日志获取线程"
    update = QtCore.pyqtSignal(str)
    def __init__(self, exUtil:myExcel):
        super().__init__()
        self.exUtil = exUtil

    def run(self):
        while True:
            try:
                msgs = self.exUtil.resvLog()
                if isinstance(msgs, str):
                    if msgs.find("Connection refused"):
                        raise Exception("Connection refused")
                    msgs = [msgs]
                if isinstance(msgs, dict):
                    text = str(msgs)
                    if msgs.find("Connection refused"):
                        raise Exception("Connection refused")
                    msgs = [msgs]
                for msg in msgs:
                    self.update.emit(str(msg))
                    time.sleep(1)
                    continue
                time.sleep(5)
            except Exception as e:
                traceback.print_exc()
                self.update.emit("CLOSE")
                return

def win():
    app = QApplication(sys.argv)
    w = myWind()
    w.show()
    sys.exit(app.exec_())

def main():
    #CStes()
    try:
        win()
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    main()
