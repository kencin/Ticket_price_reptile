#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# RaspberryGPIO - control.py
# 2018/12/20 22:57
# Author:Kencin <myzincx@gmail.com>

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import MQTT.config as config
import json
import multiprocessing
import toDatabase
from GetTicketInfomation import getTicket
import time
import random
from AirInfo import checkAirInfo

class Control(object):

    def __init__(self):
        # print("连接MQTT初始化中...")
        pass

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(topic="lowestprice", qos=1)
        client.subscribe(topic="monitorticket", qos=1)
        client.subscribe(topic="monitorticket2", qos=1)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload, encoding="utf-8"))
        if msg.topic == "lowestprice":      # 最低价格
            a = json.loads(msg.payload)
            # the_list = getTicket.get_oneDayInfo(a[0],a[1],a[2])
            p = multiprocessing.Process(target=self.get_price, args=(a[0], a[1], a[2],))
            p.start()
        if msg.topic == "monitorticket":    # 机票监控
            a = json.loads(msg.payload)
            p = multiprocessing.Process(target=self.monitor_ticket, args=(a[0], a[1], a[2],))
            p.start()
        if msg.topic == "monitorticket2":    # 通过航班号进行机票监控
            a = json.loads(msg.payload)
            p = multiprocessing.Process(target=self. monitor_ticket_by_flight, args=(a[0], a[1], a[2], a[3]))
            p.start()

    def monitor_ticket_by_flight(self, from_city, to_city, date, flight, notStart=1):
        if notStart:
            if not checkAirInfo.check(from_city, to_city, date, flight):
                publish.single("monitorLowestPrice", payload="error", hostname=config.HOST,
                               auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
                return
        db = toDatabase.Monitor(from_city, to_city, date)
        the_list = []
        first = True
        try:
            if notStart and db.check_exits(flight):
                publish.single("monitorLowestPrice", payload="exits", hostname=config.HOST,
                               auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
                return  # 已经存在则中止这个进程
            else:
                if notStart:
                    db.insert(flight)     # 不存在则插入
        except Exception as e:
            publish.single("monitorLowestPrice", payload="error", hostname=config.HOST,
                           auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
            print(e)
            return  # 出错中止进程
        while True:
            # 如果flag为0，则中止此进程
            if db.get_flag(flight)[0] == 0:
                return
            if not first:
                the_list = getTicket.get_oneDayInfo(from_city, to_city, date)  # 获取这一天所有机票信息
            if not notStart:
                the_list = getTicket.get_oneDayInfo(from_city, to_city, date)  # 获取这一天所有机票信息
            first = False
            for i in the_list:
                if str(i.get('航班')) == flight:
                    info_list = i

            # 如果当前时间大于出发时间，则停止这个监控进程，并设置flag为0
            try:
                if time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) > info_list.get('出发时间'):
                    db.set_flag(the_list[0].get('航班'))
                    return
            except Exception as e:
                print("监控机票的时间判断出出错！错误原因：" + str(e))


            try:
                # 如果机票价格有改变
                price = db.check_exits(flight)[0]
                if info_list.get('最低票价(不含机建燃油费)') != price:
                    data = {
                        'flight':
                            info_list.get('航班'),
                        'from':
                            info_list.get('来自'),
                        'depTime':
                            info_list.get('出发时间'),
                        'arrTime':
                            info_list.get('到达时间'),
                        'beforePrice':
                            price,
                        'price':
                            info_list.get('最低票价(不含机建燃油费)'),
                        'from_city':
                            info_list.get('出发地区'),
                        'to_city':
                            info_list.get('到达地区')
                    }
                    publish.single("monitorLowestPrice", payload=str(data), hostname=config.HOST,
                                   auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
                    db.update_by_flight(info_list.get('最低票价(不含机建燃油费)'), flight)
            except Exception as e:
                # 出错发布error
                publish.single("monitorLowestPrice", payload="error", hostname=config.HOST,
                               auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
                print(e)
            time.sleep(random.randrange(600, 1800))    # 随机休眠10分钟到30分钟

    def monitor_ticket(self, from_city, to_city, date):
        if not checkAirInfo.check(from_city, to_city, date):
            publish.single("monitorLowestPrice", payload="error", hostname=config.HOST,
                           auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
            return
        first = True
        db = toDatabase.Monitor(from_city, to_city, date)
        # 检测要监控的机票价格是否已经在数据库中存在
        try:
            the_list = getTicket.get_oneDayInfo(from_city, to_city, date)  # 获取这一天所有机票信息
            if db.check_exits(the_list[0].get('航班')):
                publish.single("monitorLowestPrice", payload="exits", hostname=config.HOST,
                               auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
                return  # 已经存在则中止这个进程
            else:
                db.insert(the_list[0].get('航班'))     # 不存在则插入
        except Exception as e:
            publish.single("monitorLowestPrice", payload="error", hostname=config.HOST,
                           auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
            print(e)
            return  # 出错中止进程
        while True:
            if not first:
                the_list = getTicket.get_oneDayInfo(from_city, to_city, date)   # 获取这一天机票价格的最低值
            first = False
            # 如果flag为0，则中止此进程
            if db.get_flag(the_list[0].get('航班')) == 0:
                return

            # 如果当前时间大于出发时间，则停止这个监控进程，并设置flag为0
            if time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) > the_list[0].get('出发时间'):
                db.set_flag(the_list[0].get('航班'))
                return

            # 如果机票价格有改变
            price = db.check_exits(the_list[0].get('航班'))[0]

            try:
                if the_list[0].get('最低票价(不含机建燃油费)') != price:
                    data = {
                        'flight':
                            the_list[0].get('航班'),
                        'from':
                            the_list[0].get('来自'),
                        'depTime':
                            the_list[0].get('出发时间'),
                        'arrTime':
                            the_list[0].get('到达时间'),
                        'beforePrice':
                            price,
                        'price':
                            the_list[0].get('最低票价(不含机建燃油费)'),
                        'from_city':
                            the_list[0].get('出发地区'),
                        'to_city':
                            the_list[0].get('到达地区')
                    }
                    publish.single("monitorLowestPrice", payload=str(data), hostname=config.HOST,
                                   auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
                    db.update_by_flight(the_list[0].get('最低票价(不含机建燃油费)'), the_list[0].get('航班'))  # 价格改变后更新数据库
            except Exception as e:
                # 出错发布error
                publish.single("monitorLowestPrice", payload="error", hostname=config.HOST,
                               auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
                print(e)
            time.sleep(random.randrange(600, 1800))    # 随机休眠10分钟到30分钟

    def get_price(self, from_city, to_city, date):
        if not checkAirInfo.check(from_city, to_city, date):
            publish.single("theLowestPrice", payload="error", hostname=config.HOST,
                           auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
            return
        the_list = getTicket.get_oneDayInfo(from_city, to_city, date)  # 获取这一天机票价格的最低值
        try:
            print(the_list[0].get('最低票价(不含机建燃油费)'))
            data = {
                'flight':
                    the_list[0].get('航班'),
                'from':
                    the_list[0].get('来自'),
                'depTime':
                    the_list[0].get('出发时间'),
                'arrTime':
                    the_list[0].get('到达时间'),
                'price':
                    the_list[0].get('最低票价(不含机建燃油费)')
            }
            publish.single("theLowestPrice", payload=str(data), hostname=config.HOST,
                           auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
            # print(the_list.get()[0].get('最低票价(不含机建燃油费)'))
        except Exception as e:
            #  出错发布error
            publish.single("theLowestPrice", payload="error", hostname=config.HOST,
                           auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
            print(e)

    def get_xcMonth(self, from_city, to_city):
        db = toDatabase.ToSingleTicket()
        while True:
            the_list = getTicket.get_moreDayInfo(from_city, to_city, 5)
            db.to_sql(the_list, 'xcticket')
            time.sleep(3600)    # 休眠一小时

    def on_start(self):
        #  检测是否在数据库中已有检测队列
        process_list = []
        the_list = []
        db = toDatabase.Monitor()
        the_info = db.select_all()
        for i in the_info:
            data = {
                'flight': i[0],
                'from': i[1],
                'to': i[2],
                'depTime': str(i[3]),
                'price': i[4]
            }
            the_list.append(data.copy())
        for i in the_list:
            p = multiprocessing.Process(target=self.monitor_ticket_by_flight, args=(i.get('from'),
                                                                          i.get('to'), i.get('depTime'),
                                                                                    i.get('flight'), 0))
            process_list.append(p)
        for i in process_list:
            time.sleep(10)
            i.start()

    def connect(self):
        client = mqtt.Client(client_id="", clean_session=True, userdata=None, transport="tcp")
        client.username_pw_set(config.MQTT_USERNAME, password=config.MQTT_PASSWORD)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(config.HOST, 1883, 60)
        self.on_start()
        p = multiprocessing.Process(target=self.get_xcMonth, args=('济南', '长沙'))     # 监控进程1
        q = multiprocessing.Process(target=self.get_xcMonth, args=('长沙', '济南'))     # 监控进程2
        p.start()
        q.start()
        client.loop_forever()

