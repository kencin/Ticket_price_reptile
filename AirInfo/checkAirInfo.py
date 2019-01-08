#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# getTicketInfo - checkAirInfo.py
# 2019/1/8 15:02
# Author:Kencin <myzincx@gmail.com>

import json
import time
from GetTicketInfomation import getTicket


def check(from_city, to_city, dep_time, flight=None):

    # 通过cities文件判断城市是否合法
    with open('./config/citys.json', 'r', encoding="UTF-8") as f:
        file = f.read()
        cities = json.loads(file)
        if from_city not in cities:
            return False
        if to_city not in cities:
            return False

    # 通过time函数判断时间合法性
    try:
        if ":" in dep_time:
            time.strptime(dep_time, "%Y-%m-%d %H:%M:%S")
        else:
            time.strptime(dep_time, "%Y-%m-%d")
    except ValueError:
        return False

    # 通过航班查询判断航班号的合法性
    if flight is not None:
        the_list = getTicket.get_oneDayInfo(from_city, to_city, dep_time)  # 获取这一天所有机票信息
        for i in the_list:
            if flight in i.get('航班'):
                return True
        return False
    return True
