#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# monitorTicket - main.py
# 2019/1/4 10:32
# Author:Kencin <myzincx@gmail.com>
import time
import multiprocessing
from GetTicketInfomation import getTicket
import toDatabase
import MQTT.control

# 主函数
def main():
    db = toDatabase.ToSingleTicket()
    city1 = '济南'
    city2 = '长沙'
    pool = multiprocessing.Pool(processes=2)
    result1 = pool.apply_async(getTicket.get_moreDayInfo, args=(city1, city2, 30))
    result2 = pool.apply_async(getTicket.get_moreDayInfo, args=(city2, city1, 30))
    pool.close()
    pool.join()
    pool2 = multiprocessing.Pool(processes=2)
    pool2.apply_async(db.to_sql, args=(result1.get(), 'firstticket'))
    pool2.apply_async(db.to_sql, args=(result2.get(), 'secondticket'))
    pool2.close()
    pool2.join()
    # the_list = get_oneDayInfo(city1, city2,'2019-01-17')
    # for i in the_list:
    #     print(i)


if __name__ == '__main__':
    control = MQTT.control.Control()
    control.connect()
    # main()


