#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# monitorTicket - getTicket.py
# 2019/1/6 15:36
# Author:Kencin <myzincx@gmail.com>
import datetime
import json
import requests
import GetTicketInfomation as gt
import time


# 获取n天的日期，并以列表形式返回
def get_days(days):
    allDays = []
    # 现在的时间
    now = datetime.datetime.now()
    # 递增的时间
    delta = datetime.timedelta(days=1)
    # n天后的时间
    endnow = now + datetime.timedelta(days=days)
    # n天后的时间转换成字符串
    endnow = str(endnow.strftime('%Y-%m-%d'))
    offset = now
    # 当日期增加到六天后的日期，循环结束
    while str(offset.strftime('%Y-%m-%d')) != endnow:
        allDays.append(str(offset.strftime('%Y-%m-%d')))
        offset += delta
    return allDays


# 获取一个proxy
def get_proxy():
    return requests.get("http://120.25.149.0:8080/get/").content


# 获取所有proxy
def get_allPorxy():
    return json.loads(requests.get("http://120.25.149.0:8080/get_all/").content)


# 获取单独一天的机票信息
def get_oneDayInfo(from_city, to_city, start_date, the_proxy=get_proxy(), end_date=None):
    the_list = []
    try:
        # 飞猪旅行
        for item in gt.fz.get_message_fz(from_city, to_city, start_date, the_proxy):
            the_list.append(item)
        # 携程旅行
        for item in gt.xc.get_message_xc(from_city, to_city, start_date, the_proxy):
            the_list.append(item)
        # 京东旅行
        for item in gt.jd.get_message_jd(from_city, to_city, start_date, the_proxy):
            the_list.append(item)
        the_list.sort(key=lambda item: item['最低票价(不含机建燃油费)'])
    except Exception as e:
        print(e)
    # 按价格从低到高排序
    return the_list


# 获取n天的机票信息
def get_moreDayInfo(from_city, to_city, dayNumber):
    the_list = []
    for day, proxy in zip(get_days(dayNumber), get_allPorxy()):
        # 飞猪旅行 多次查询被封禁，固不适用
        # for item in gt.fz.get_message_fz(from_city, to_city, day, proxy):
        #     the_list.append(item)
        # 携程旅行
        for item in gt.xc.get_message_xc(from_city, to_city, day, proxy):
            the_list.append(item)
        # 京东旅行 没有HTTPS代理，固不适用
        # for item in gt.jd.get_message_jd(from_city, to_city, day, proxy):
        #     the_list.append(item)
        time.sleep(5)
        print(day + "的机票信息已获取")
    return the_list

if __name__ == '__main__':
    the_list = get_oneDayInfo('济南', '长沙', '2019-01-17')
    print(the_list)
    for i in the_list:
        if str(i.get('航班')) == '昆明航空KY8234':
            print(i)
