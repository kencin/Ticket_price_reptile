#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# monitorTicket - jd.py
# 2019/1/4 17:23
# Author:Kencin <myzincx@gmail.com>
"""
京东机票信息获取
URL = https://jipiao.jd.com/search/queryFlight.action
采用GET 获得
"""

import requests
from datetime import datetime
from AirInfo import getAirInfo
from GetTicketInfomation import getTicket

def makeTime(depTime, arrTime, day):
    depHour = str(depTime)[0:2]
    depMin = str(depTime)[2:4]
    arrHour = str(arrTime)[0:2]
    arrMin = str(arrTime)[2:4]
    year_s, mon_s, day_s = day.split('-')
    depT = datetime(int(year_s), int(mon_s), int(day_s), int(depHour), int(depMin))
    arrT = datetime(int(year_s), int(mon_s), int(day_s), int(arrHour), int(arrMin))
    return depT, arrT


def get_message_jd(from_city, to_city, start_date, proxy=None):
    if len(start_date)>10:
        start_date = str(start_date)[0:10]
    headers = {
        'Host': "jipiao.jd.com",
        'Accept-Language': "zh-CN,zh;q=0.8,en;q=0.6",
        'Accept-Encoding': "gzip, deflate, br",
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': "keep-alive",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.98 Safari/537.36'
    }
    payload = {
        'depCity': from_city,
        'arrCity': to_city,
        'depDate': start_date,
        'arrDate': start_date,
        'queryModule': '1',
        'lineType': 'OW',
        'queryType': 'jipiaoindexquery'
    }
    if str(proxy)[0] == 'b':
        a = str(proxy).split("'")
        proxy = {
            'http': 'http://' + a[1]
        }
    else:
        proxy = {"http": "http://{}".format(proxy)}
    url = 'https://jipiao.jd.com/search/queryFlight.action'
    try:
        times = 4
        response = requests.get(url, params=payload, headers=headers,
                                proxies=proxy).json()
        while response['data']['flights'] is None and times > 0:
            response = requests.get(url, params=payload, headers=headers,
                                    proxies=proxy).json()
            times -= 1
    except Exception as e:
        print("no1. 京东查询失败！ 错误原因：" + str(e))
        return
    flights = response.get('data').get('flights')
    # print(routeLists)
    try:
        for flight in flights:
            depTime, arrTime = makeTime(flight['depTime'], flight['depTime'], start_date)
            airinfo = getAirInfo.getAirInfo(flight['depCity'], flight['arrCity'], flight['airways'])
            dic = {
                'depTime': str(depTime),
                'arrTime': str(arrTime)
            }
            yield {  # 构造生成器
                '来自': '京东旅行',
                '航班': airinfo['cname'] + flight['flightNo'],  # 航班
                '出发机场': airinfo['from_airport_name'],  # 出发机场
                '出发地区': airinfo['from_province'] + airinfo['from_area'],
                '到达机场': airinfo['to_airport_name'],  # 到达机场
                '到达地区': airinfo['to_province'] + airinfo['to_area'],
                '出发时间': dic['depTime'],  # 出发时间
                '到达时间': dic['arrTime'],  # 到达时间
                '最低票价(不含机建燃油费)': int(flight['bingoLeastClassInfo']['price'])  # 最低票价
            }
        print("京东查询成功！")
    except Exception as e:
        print('no2. 京东查询失败！ 错误原因：' + str(e))


if __name__ == '__main__':
    from_city = '济南'
    to_city = '长沙'
    date = '2019-01-11 00:00:00'
    the_list = []
    for item in get_message_jd(from_city, to_city, date, getTicket.get_proxy()):
        the_list.append(item)
    for item in the_list:
        print(item)