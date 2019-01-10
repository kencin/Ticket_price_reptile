#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# monitorTicket - xc.py
# 2019/1/4 17:23
# Author:Kencin <myzincx@gmail.com>
"""
携程机票信息获取
URL = http://flights.ctrip.com/itinerary/api/12808/products
采用POST + COOKIES 获得
"""

import requests
import json
from AirInfo import getAirInfo
from GetTicketInfomation import getTicket


# post传递相应的数据，数据从get_xcelement()函数得到
def get_message_xc(from_city, to_city, start_date, proxy=None):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.98 Safari/537.36',
        'Host': 'flights.ctrip.com',
        'Content-Type': 'application/json',
    }
    with open('./config/citys.json', 'r', encoding="UTF-8") as f:
        file = f.read()
        city = json.loads(file)
        fcity = city[from_city].lower()
        tcity = city[to_city].lower()
    with open('./config/cityid.json', 'r', encoding="UTF-8") as f:
        file = f.read()
        cityid = json.loads(file)
        fctiy_id = int(cityid[from_city])
        tcity_id = int(cityid[to_city])
    cookies = {}  # 初始化cookies字典变量
    with open(r'./config/xccookies.txt', 'r') as f:
        for line in f.read().split(';'):  # 按照字符：进行划分读取
            name, value = line.strip().split('=', 1)  # 其设置为1就会把字符串拆分成2份
            cookies[name] = value  # 为字典cookies添加内容
    # 构造post传递的数据
    payloadData = {
        "flightWay": "Oneway",
        "classType": "ALL",
        "hasChild": 'false',
        "hasBaby": 'false',
        "searchIndex": 1,
        "airportParams": [{"dcity": fcity, "acity": tcity, "dcityname":from_city, "acityname":to_city,
                          "date": start_date, "dcityid": fctiy_id, "acityid": tcity_id}]
    }
    if str(proxy)[0] == 'b':
        a = str(proxy).split("'")
        proxy = {
            'http': 'http://' + a[1]
        }
    else:
        proxy = {"http": "http://{}".format(proxy)}
    url = 'http://flights.ctrip.com/itinerary/api/12808/products'
    dumpJsonData = json.dumps(payloadData)                                      # 转换为字符串
    try:
        response = requests.post(url, data=dumpJsonData, headers=headers, cookies=cookies,
                                 proxies=proxy).json()  # 带上数据发送请求，获取json格式的信息
        pass
    except Exception as e:
        print("携程代理查询失败！")
        try:
            print("携程尝试常规查询！")
            # 带上数据发送请求，获取json格式的信息
            response = requests.post(url, data=dumpJsonData, headers=headers, cookies=cookies,).json()
        except Exception as e:
            print("携程常规查询也失败了！")
            print(e)
            return
    # 提取有用信息
    routeLists = response.get('data').get('routeList')
    try:
        for routeList in routeLists:
            if routeList.get('routeType') == 'Flight':  # 不包含飞机加火车的路线

                legs = routeList.get('legs')[0]
                flight = legs['flight']
                characteristic = legs['characteristic']
                airinfo = getAirInfo.getAirInfo(flight['departureAirportInfo']['airportTlc'],
                                                flight['arrivalAirportInfo']['airportTlc'], flight['airlineCode'])
                yield {  # 构造生成器
                    '来自': '携程旅行',
                    '航班': flight['airlineName'] + flight['flightNumber'],  # 航班
                    '共享航班': flight['sharedFlightName'],  # 共享航班
                    '出发机场': airinfo['from_airport_name'],  # 出发机场
                    '出发地区': airinfo['from_province'] + airinfo['from_area'],
                    '到达机场': airinfo['to_airport_name'],  # 到达机场
                    '到达地区': airinfo['to_province'] + airinfo['to_area'],
                    '出发时间': flight['departureDate'],  # 出发时间
                    '到达时间': flight['arrivalDate'],  # 到达时间
                    '机型': flight['craftTypeName'],
                    '种类': flight['craftTypeKindDisplayName'],
                    '延误率': flight['punctualityRate'],
                    '最低票价(不含机建燃油费)': int(characteristic['lowestPrice'])  # 最低票价
                }
        print("携程查询成功！")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    from_city = '济南'
    to_city = '长沙'
    date = '2019-01-07'
    the_list = []
    proxy = getTicket.get_proxy()
    for item in get_message_xc(from_city, to_city, date, proxy):
        the_list.append(item)
    for item in the_list:
        print(item)

