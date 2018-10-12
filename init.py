
# -*- coding: utf-8 -*- 

import  xdrlib, sys, json
import xlrd

strategy="/home/pw/pw_service/mysql/config.txt"
strategy_dir="/home/pw/pw_service/mysql/"

V="varchar(32)"
F="float(8, 2)"
I="int(13)"
D="DATETIME"

def parse_head(t_name, row, b_ColNum, e_ColNum, t_list):
    # print(row)
    title=[]
    for no in range(b_ColNum, e_ColNum + 1):
        title.append(row[no])

    create_mysql_table(t_name, title, t_list)

# [title1 title2 title3]
# V|F|F
def create_mysql_table(t_name, title, t_list):

    cmd = "CREATE TABLE IF NOT EXISTS " + t_name + "(";

    for no in range(len(title)):
        # print("title: ", title[no], ", type", t_list[no])
        cmd += title[no] + " " + eval(t_list[no])

        if(no != len(title) - 1):
            cmd += ', '

    cmd += ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"

    print(cmd)


def parse_body(t_name, row, b_ColNum, e_ColNum, t_list):
    # print(row)
    body=[]

    for no in range(b_ColNum, e_ColNum + 1):
        if t_list[no] == 'V' or t_list[no] == 'D':
            body.append('\'' + str(row[no]) + '\'')
        elif t_list[no] == 'I':
            body.append(int(row[no]))
        else: # float
            body.append(row[no])

    insert_mysql_table(t_name, body)

def insert_mysql_table(t_name, body):
    cmd = "INSERT INTO " + t_name + " VALUES(";
    for no in range(len(body)):
        cmd += str(body[no])

        if(no != len(body) - 1):
            cmd += ', '

    cmd += ");"

    print(cmd)

def parse_excel(s_name, t_name, t_RowNum, b_RowNum, e_RowNum, b_ColNum, e_ColNum, t_list):

    # print(s_name, t_name, b_RowNum, e_RowNum, b_ColNum, e_colNum, t_list)

    data = xlrd.open_workbook(strategy_dir + s_name) # "obj.xlsx"
    table = data.sheets()[0]

    row_head = table.row_values(t_RowNum)
    parse_head(t_name, row_head, b_ColNum, e_ColNum, t_list)

    for no in range(b_RowNum, e_RowNum+1):
        row_body = table.row_values(no)
        parse_body(t_name, row_body, b_ColNum, e_ColNum, t_list)

def parse_line(d):

    s_name = d["S_NAME"]
    t_name = d["T_NAME"]

    t_RowNum = d["t_RowNum"]-1

    b_RowNum = d["b_RowNum"]-1
    e_RowNum = d["e_RowNum"]-1

    b_ColNum = d["b_ColNum"]-1
    e_ColNum = d["e_ColNum"]-1

    t_List = d["t_list"].split('|')

    parse_excel(s_name, t_name, t_RowNum, b_RowNum, e_RowNum, b_ColNum, e_ColNum, t_List)

def main():
    with open(strategy) as f:
        for l in f.readlines():
            line = l.strip('\n')
            # print(line)
            d=json.loads(line)
            parse_line(d)
            # print(d)

if __name__=="__main__":
    main()


