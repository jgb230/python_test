#!/usr/bin/env python
# coding=utf-8
import  xdrlib, sys, json
import xlrd

import pymysql

reload(sys)
sys.setdefaultencoding('utf-8')

brow=2
maxrow=187
bcol=2
maxcol=7

motiveFile="/home/jgb/python/motive/motive0423.xlsx"

g_host='172.16.0.11'
g_port=3306
g_user='root'
g_passwd='12345678'
g_db='tesdb001'
g_charset='utf8'

db = pymysql.connect(host=g_host, port=g_port, user=g_user, passwd=g_passwd, db=g_db, charset=g_charset)
data = xlrd.open_workbook(motiveFile)

esql = "SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA=\'"+ g_db +"\' AND TABLE_NAME='tb_element';"
gsql = "SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA=\'"+ g_db +"\' AND TABLE_NAME='tb_element_group';"
msql = "SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA=\'"+ g_db +"\' AND TABLE_NAME='tb_motive';"

einsert = "insert into tb_element (id, description, status) values ("
ginsert = "INSERT INTO tb_element_group (id, sequence, element_id, status) VALUES ("
minsert = "INSERT INTO tb_motive (object, dim, value, motive_group, desire_group, love_group, status) VALUES ("

einsertmany = "insert into tb_element (id, description, status) values (%s, %s, %s)"
ginsertmany = "INSERT INTO tb_element_group (id, sequence, element_id, status) VALUES (%s, %s, %s, %s)"
minsertmany = "INSERT INTO tb_motive (object, dim, value, motive_group, desire_group, love_group, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"

etruncate = "truncate table tb_element;"
gtruncate = "truncate table tb_element_group;"
mtruncate = "truncate table tb_motive;"

dmElement = ['可乐', '橙汁', '咖啡', '奶茶', '椰子汁', '蓝莓汁', '幻幻果汁', '方便面', '火腿肠', '饭团', '三明治', '话梅', 
'薯片', '巧克力', '苹果', '梨子', '芒果', '蓝莓', '幻幻果实', '卡布奇诺蛋糕', '巧克力森林', '芒果奶油蛋糕', '冰淇淋', 
'荔枝布丁', '棒冰', '蓝色多瑙河', 'G小调', '咏叹调', '晒太阳']

status = ['动机','渴望','喜好']

elements = []
groups = []

groupBegin = 0

def excuteSql(sqlcmd):
    cursor = db.cursor()
    next = 0
    try:
        cursor.execute(sqlcmd)
        db.commit()
        cursor.close()
    except:
        print("error")
    return next

def excuteManySql(sqlcmd,parmList):
    cursor = db.cursor()
    next = 0
    try:
        cursor.executemany(sqlcmd,parmList)
        db.commit()
        cursor.close()
    except:
        print("error")
    return next

def truncate():
    excuteSql(etruncate)
    excuteSql(gtruncate)
    excuteSql(mtruncate)

def getEnextId():
    cursor = db.cursor()
    next = 0
    try:
        cursor.execute(esql)
        results = cursor.fetchall()
        for rw in results:
            next=rw[0]
        cursor.close()
    except:
        print("error")
    return next

def getGnextId():
    cursor = db.cursor()
    next = 0
    try:
        cursor.execute(gsql)
        results = cursor.fetchall()
        for rw in results:
            next=rw[0]
        cursor.close()
    except:
        print("error")
    return next

def parseExcel():
    table = data.sheets()[0]
    for rw in range(0, maxrow):
        row = table.row_values(rw)
        cmd = ""
        for cl in range(0, maxcol):
            colstr = str(row[cl])
            cmd += colstr
            try:
                colstr.index("|")
            except :
                cmd += "-+-"
            else:
                cmd += "---"
            cmd += ", "
        print(cmd)

def parseElements():
    table = data.sheets()[0]
    for rw in range(brow, maxrow):
        row = table.row_values(rw)
        elements.append(row[1])
        groups.append(row[1])

def parseGroup():
    global groups
    table = data.sheets()[0]
    tempgroup = []
    for rw in range(brow, maxrow):
        row = table.row_values(rw)
        for cl in range(bcol,maxcol):
            colstr = str(row[cl])
            try:
                colstr.index("|")
            except:
                temp=""
            else:
                tempgroup.append(row[cl])
    for i in tempgroup:
        if i not in groups:
            groups.append(i)

def buildElemts():
    begin = getEnextId()
    sqlparm = []
    for rw in elements:
        rowlist = []
        statu = 0
        element = "\"" + rw + "\""
        cmd = einsert
        cmd += str(begin) + "," + element + "," 
        try:
            dmElement.index(rw)
        except ValueError:
            statu = 0
        else:
            statu = 2

        rowlist.append(begin)
        rowlist.append(rw)
        rowlist.append(statu)
        cmd += str(statu) + ");"
        begin += 1
        #print(cmd)
        sqlparm.append(rowlist)
    excuteManySql(einsertmany, sqlparm)

def buildGroup():
    global groupBegin
    begin = getGnextId()
    sqlparm = []
    print("groupBegin:" + str(groupBegin))
    for group in groups:
        temps = group.split("|")
        seq=1
        for temp in temps:
            rowlist = []
            cmd = ginsert
            try:
                elements.index(temp)
            except:
                print("error:"+temp+"not in elements")
                exit
            cmd += str(begin).strip() + "," + str(seq).strip() + "," + str(elements.index(temp)+1).strip() + "," + "0);"
            rowlist.append(begin)
            rowlist.append(seq)
            rowlist.append(str(elements.index(temp)+1).strip())
            rowlist.append(0)
            sqlparm.append(rowlist)
            seq+=1
            #print(cmd)
        begin += 1
    excuteManySql(ginsertmany, sqlparm)

def buildMotive():
    table = data.sheets()[0]
    sqlparm = []
    for rw in range(brow, maxrow):
        rowlist = []
        row = table.row_values(rw)
        cmd = minsert
        cl3 = str(row[3]).strip() if len(str(row[3]).strip())>0 else "0"
        cmd += str(elements.index(row[1])+1).strip() + "," + str(status.index(row[2])+1).strip() + "," + cl3 + "," 

        rowlist.append(str(elements.index(row[1])+1).strip())
        rowlist.append(str(status.index(row[2])+1).strip())
        rowlist.append(cl3)
        for cl in range(4,7):
            try:
                idx=groups.index(row[cl])+1
            except:
                idx=0
            cmd += str(idx).strip() + "," 
            rowlist.append(str(idx).strip())
        cmd += "0);"
        rowlist.append(0)
        sqlparm.append(rowlist)
        #print(cmd)
    excuteManySql(minsertmany, sqlparm)

def main():
    #parseExcel()
    truncate()
    parseElements()
    parseGroup()
    print("print groups :" + str(len(groups)))
    #for i in groups:
        #print(str(i))

    print("print elements :" + str(len(elements)))
    #for i in elements:
        #print(i)
    print("element sql:")
    buildElemts()
    print("group sql:")
    buildGroup()
    print("motive sql:")
    buildMotive()
    print(getEnextId())
    print(getGnextId())

if __name__=="__main__":
    main()
    db.close()
