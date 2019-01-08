#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# monitorTicket - fz.py
# 2019/1/4 17:23
# Author:Kencin <myzincx@gmail.com>
"""
飞猪机票信息获取
采用POST + COOKIES 获得
"""

import requests
import json
from AirInfo import getAirInfo


def get_message_fz(from_city, to_city, start_date, proxy=None):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.98 Safari/537.36'
    }
    the_proxy = {
        'https': 'https://113.53.83.195:35686',
    }
    f = open(r'./config/fzcookies.txt', 'r')  # 打开所保存的cookies内容文件
    cookies = {}  # 初始化cookies字典变量
    for line in f.read().split(';'):  # 按照字符：进行划分读取
        name, value = line.strip().split('=', 1)  # 其设置为1就会把字符串拆分成2份
        cookies[name] = value  # 为字典cookies添加内容
    url = 'https://sjipiao.fliggy.com/searchow/search.htm'
    payload = {'depCityName': from_city, 'arrCityName': to_city, 'depDate': start_date, '_input_charset': 'utf-8'}
    message = requests.get(url, params=payload, headers=headers, cookies=cookies,
                           proxies={"http": "http://{}".format(proxy)}).text
    # message = message.strip()  # 去除首尾空字符串
    # message = message[1:-2]  # 将首位的括号去掉，否则不能转换成json格式
    # jsons = json.loads(message)  # 转换成json格式
    try:
        message = requests.get(url, params=payload, headers=headers, cookies=cookies,
                               proxies={"http": "http://{}".format(proxy)}).text
        message = message.strip()  # 去除首尾空字符串
        message = message[1:-2]  # 将首位的括号去掉，否则不能转换成json格式
        jsons = json.loads(message)  # 转换成json格式
    except Exception as e:
        print("飞猪查询失败！")
        print(e)
        return
    if jsons.get('data'):
        jsons = jsons.get('data')
        flights = jsons.get('flight')
        for flight in flights:                       # 生成器
            airinfo = getAirInfo.getAirInfo(flight.get('depAirport'), flight.get('arrAirport'),
                                            flight.get('airlineCode'))
            times = {
                'depTime': str(flight.get('depTime'))+':00',
                'arrTime': str(flight.get('arrTime'))+':00'
            }
            yield {
                '来自': '飞猪旅行',
                '航班': airinfo['cname']+flight.get('flightNo'),          # 航空公司及航班
                '出发机场': airinfo['from_airport_name'],  # 出发机场
                '出发地区': airinfo['from_province'] + airinfo['from_area'],
                '到达机场': airinfo['to_airport_name'],  # 到达机场
                '到达地区': airinfo['to_province'] + airinfo['to_area'],
                '出发时间': times['depTime'],                                       # 出发时间
                '到达时间': times['arrTime'],                                       # 到达时间
                '最低票价(不含机建燃油费)': int(flight.get('cabin').get('price'))         # 最低票价
            }


if __name__ == '__main__':
    from_city = '济南'
    to_city = '长沙'
    date = '2019-01-17'
    list = []
    for item in get_message_fz(from_city, to_city, date):
        list.append(item)
    for item in list:
        print(item)