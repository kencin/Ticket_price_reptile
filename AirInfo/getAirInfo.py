#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# monitorTicket - getAirInfo.py
# 2019/1/4 23:08
# Author:Kencin <myzincx@gmail.com>
import json


def getAirInfo(from_threenumber, to_threenumber, carrierCode):
    from_airport_name = 'Wrong'
    from_province = 'Wrong'
    from_area = 'Wrong'
    to_airport_name = 'Wrong'
    to_province = 'Wrong'
    to_area = 'Wrong'
    cname = 'Wrong'
    with open('./config/airport.json', 'r', encoding="UTF-8") as f:
        file = f.read()
        airports = json.loads(file)
        for airport in airports['airport']:
            if airport.get('三字码') == from_threenumber:
                from_province = airport.get('所属省份')
                from_area = airport.get('服务地区')
                from_airport_name = airport.get('中文名称')
            if airport.get('三字码') == to_threenumber:
                to_province = airport.get('所属省份')
                to_area = airport.get('服务地区')
                to_airport_name = airport.get('中文名称')
    with open('./config/airlines.json', 'r', encoding="UTF-8") as f:
        file = f.read()
        airlines = json.loads(file)
        for airline in airlines['airplaneData']:
            if airline.get('carrierCode') == carrierCode:
                cname = airline.get('cName')

    info = {
        'from_airport_name': from_airport_name,
        'from_province': from_province,
        'from_area': from_area,
        'to_airport_name': to_airport_name,
        'to_province': to_province,
        'to_area': to_area,
        'cname': cname
    }
    return info
