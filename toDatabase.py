#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# monitorTicket - toDatabase.py
# 2019/1/6 12:18
# Author:Kencin <myzincx@gmail.com>
from config import database as config
import pymysql
import time


class ToSingleTicket(object):
    def __init__(self):
        pass

    def to_sql(self, the_list, the_table):   # 插入某一单一数据库，如携程专属或飞猪专属数据库
        db = pymysql.connect(config.HOST, config.Username, config.Password, config.Database_name)
        cursor = db.cursor()
        for i in the_list:
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # 插入语句
            sql = "INSERT INTO %s VALUES ('%s', '%s', %d,'%s', '%s', '%s', '%s', '%s','%s')"% (the_table, i.get('出发时间'),
                  i.get('到达时间'), i.get('最低票价(不含机建燃油费)'), i.get('航班'), i.get('出发机场'), i.get('出发地区'),
                  i.get('到达机场'), i.get('到达地区'), now)

            # 判断是否存在语句
            isExit = "SELECT price FROM %s WHERE  " \
                     "depTime = '%s' AND flight = '%s'" % (the_table, i.get('出发时间'), i.get('航班'))
            try:
                cursor.execute(isExit)
                price = cursor.fetchall()
                if len(price) is 0:   # 不存在则直接插入
                    cursor.execute(sql)
                    db.commit()
                else:
                    price = price[-1][0]  # 取得最近一次的价格
                    if price != i.get('最低票价(不含机建燃油费)'):  # 存在且价格不同才插入，否则忽略
                        cursor.execute(sql)
                        db.commit()

            except Exception as e:
                print("写入携程机票数据库失败！ 错误原因：" + str(e))
                db.close()
                return
        db.close()
        print("成功写入携程机票数据库")


class ToMixTicket(object):
    def __init__(self):
        pass

    def to_sql(self, the_list, the_table):
        db = pymysql.connect(config.HOST, config.Username, config.Password, config.Database_name)
        cursor = db.cursor()
        for i in the_list:
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # 插入语句
            sql = "INSERT INTO %s VALUES ('%s', %d, '%s', '%s', " \
                  "'%s', '%s', '%s', '%s', '%s'," \
                  "'%s')" % (
                  the_table, i.get('出发时间'),
                  i.get('到达时间'), i.get('最低票价(不含机建燃油费)'), i.get('来自'), i.get('航班'), i.get('出发机场'), i.get('出发地区'),
                  i.get('到达机场'), i.get('到达地区'), now)

            # 判断是否数据已存在
            isExit = "SELECT price FROM %s WHERE source = '%s' AND flight = '%s' AND " \
                     "depTime = '%s'" % (the_table, i.get('来自'), i.get('航班'), i.get('出发时间'))
            try:
                cursor.execute(isExit)
                price = cursor.fetchone()   # 加快效率，获取一条就行
                if price is None:  # 没有获得价格则说明在数据库中不存在， 插入即可
                    cursor.execute(sql)
                    db.commit()
                else:
                    for m in price:
                        if m != i.get('最低票价(不含机建燃油费)'):     # 价格不同则插入一个新的，价格相同则忽略本次查询
                            cursor.execute(sql)
                            db.commit()
            except Exception as e:
                print("写入混合机票数据库失败！")
                print(e)
                db.close()
                return
        db.close()
        print("混合机票数据库写入完成！")


class Monitor(object):
    table_name = 'monistorQueue'
    db = pymysql.connect(config.HOST, config.Username, config.Password, config.Database_name)
    cursor = db.cursor()

    def __init__(self, from_city=None, to_city=None, date=None):
        self.from_city = from_city
        self.to_city = to_city
        self.date = date

    def check_exits(self, flight=None):
        if flight is not None:
            sql = "SELECT price FROM %s WHERE fromArea = '%s' AND toArea = '%s' AND depTime = '%s' AND flight = '%s'" % \
                  (self.table_name, self.from_city, self.to_city, self.date, flight)
        else:
            sql = "SELECT price FROM %s WHERE fromArea = '%s' AND toArea = '%s' AND depTime = '%s'" % \
                  (self.table_name, self.from_city, self.to_city, self.date)
        try:
            self.cursor.execute(sql)
            price = self.cursor.fetchone()  # 加快效率，获取一条就行
            if price:
                return price
            else:
                return False
        except Exception as e:  # 出现错误，则返回已存在，以便退出监控进程
            print("check_exits 函数出错！")
            print(e)
            self.db.close()
            return True

    def insert(self, flight=None):
        if flight is None:
            sql = "INSERT INTO %s (fromArea, toArea, depTime, price) " \
                  "VALUES ('%s', '%s', '%s', '%d')" % (self.table_name, self.from_city, self.to_city, self.date, 0)
        else:
            sql = "INSERT INTO %s (fromArea, toArea, depTime, price, flight) " \
                  "VALUES ('%s', '%s', '%s', '%d', '%s')" \
                  % (self.table_name, self.from_city, self.to_city, self.date, 0, flight)

        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print("insert 函数出错！")
            print(e)

    def update_by_flight(self, price, flight):
        price = int(price)
        sql = "UPDATE %s SET price = %d WHERE fromArea = '%s' AND toArea = '%s' " \
              "AND depTime = '%s' AND flight = '%s'" % \
              (self.table_name, price, self.from_city, self.to_city, self.date, flight)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print("update_by_flight 函数出错！")
            print(e)

    def select_all(self):
        sql = "SELECT * FROM %s" % self.table_name
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            print("se;ect_all 函数出错！")
            print(e)

    def set_flag(self, flight):
        sql = "UPDATE %s SET flag = 0 WHERE fromArea = '%s' AND toArea = '%s' AND depTime = '%s' AND flight ='%s'" % \
              (self.table_name, self.from_city, self.to_city, self.date ,flight)

        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print("set_flag 函数出错")
            print(e)

    def get_flag(self, flight):
        sql = "SELECT flag FROM %s WHERE fromArea = '%s' AND toArea = '%s' AND depTime = '%s' AND flight = '%s'" % \
             (self.table_name, self.from_city, self.to_city, self.date, flight)
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except Exception as e:
            print("get_flag 函数出错")
            print(e)
