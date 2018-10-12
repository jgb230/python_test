#!/usr/bin/env python3
# coding=utf-8

"""火车票查询

Usage:
    ticket [-gdtkz] <from> <to> <date>

Options:
    -h,--help  显示帮助菜单
    -g         高铁
    -d         动车
    -t         特快
    -k         快速
    -z         直达

Example:
    ticket  北京 上海 2018-10-10
    ticket  -dg  成都 南京  2018-10-10
"""

import re
import requests
from pprint import pprint
from docopt import docopt
from prettytable import PrettyTable
from colorama import init, Fore
import urllib3

dc={}
header = '车次 车站 时间 历时 一等 二等 高级软卧 软卧 硬卧 硬座 无座'.split()

def alltrans(trans, place, options):
    for row in trans:
        cols = row.split('|')
        no = cols[3]
        ini = no[0].lower()
        if not options or ini in options:
            train = [
                cols[3], #车次
                '\n'.join([Fore.GREEN + place[cols[6]] + Fore.RESET, #始发站
                           Fore.RED +place[cols[7]]]) + Fore.RESET, #终点站
                '\n'.join([cols[8], #发车时间
                           cols[9]]), #到站时间
                cols[10], #历时
                cols[-6] if cols[-6] else '--', #一等
                cols[-7] if cols[-7] else '--', #2等
                cols[-15] if cols[-15] else '--', #高级软
                cols[-8] if cols[-8] else '--', #软卧
                cols[-14] if cols[-14] else '--', #硬卧
                cols[-11] if cols[-11] else '--', #硬座
                cols[-9] if cols[-9] else '--', #无座
            ]
            yield train


def search(sfrom, sto, sdate, args):
    url = ('https://kyfw.12306.cn/otn/leftTicket/queryO'
            '?leftTicketDTO.train_date={}'
            '&leftTicketDTO.from_station={}'
            '&leftTicketDTO.to_station={}'
            '&purpose_codes=ADULT').format(sdate, sfrom, sto)
    res = requests.get(url, verify=False)
    place = res.json()['data']['map']
    trans = res.json()['data']['result']
    options = ''.join([
        key for key, value in args.items() if value is True
    ])
    pt = PrettyTable()
    pt._set_field_names(header)
    for i in alltrans(trans, place, options):
        pt.add_row(i)
    print(pt)


def cli():
    """command-line interface"""
    args = docopt(__doc__)
    sfrom = dc[args['<from>']]
    sto = dc[args['<to>']]
    sdate = args['<date>']
    date = sdate.split('-')
    sdate = "{0:4}-{1:0>2}-{2:0>2}".format(date[0], date[1], date[2])
    print(sdate)
    search(sfrom, sto, sdate, args)



def station():
    global dc
    url='https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9050'
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    res = requests.get(url, verify=False)
    stt = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', res.text)
    dc = dict(stt)
    #print('keys:')
    #for i in dc.keys():
        #print(i + ':' + dc.get(i))


if __name__ == '__main__':
    station()
    cli()

