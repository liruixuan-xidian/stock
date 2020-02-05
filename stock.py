#!/usr/bin/env python
# coding: utf-8

# In[6]:


import tushare as ts
import time
import sys
import pandas as pd

df = pd.read_csv("/Users/liruixuan/program/stock/stock.csv", dtype = object)


# In[7]:


#限制每日发短信数量， 。。。未完待续
def constrain_message_number():
    if message_number > 10:
        return 0
    return 1
    #TODO


# In[8]:


#利用twilio发送短信到本地手机
from twilio.rest import Client
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse
import secret_vari

def construct_message_body(stock_df):
    stock_name = list(stock_df.loc["name"].values)
    change_rate = list(stock_df.loc["涨跌(%)"].values)
    print(change_rate)
    body = str(stock_name) + " is decrease to " + str(change_rate) + " % " + "please sell it as soon as possibale."
    return body

def send_message(message):
    accound_sid = secret_vari.accound_sid
    auth_token = secret_vari.auth_token
    client =Client(accound_sid,auth_token)
    message = client.messages.create(
        to=secret_vari.my_telephone_num,
        from_=secret_vari.twilio_telephone_num,
        body=message)


# In[10]:


#获取实时股票行情， 持有股票日跌幅超过3%， 短信提醒卖出
import easyquotation
import pandas as pd

def get_stock_current(stock_code):
    quotation = easyquotation.use("qq")
    stock_current = quotation.stocks(stock_code)
    df = pd.DataFrame(stock_current)
    return df

def find_decrease_stock(stock_df):
    sell_stock = stock_df.loc[["name", "涨跌(%)"], stock_df.loc["涨跌(%)"] < -3]
    return sell_stock

def get_sell_stock(code_list):
    code_df = get_stock_current(code_list)
    sell_stock = find_decrease_stock(code_df)
    return sell_stock

#get_sell_stock(stock_code)


# In[11]:


#判断是否为交易日， 返回1为交易日，0为非交易日， 。。。未完待续
import tushare as ts
import datetime
import time
def TradingDay():
    DatetimeNOW = datetime.datetime.now().strftime('%Y-%m-%d')
    OpenList = ts.trade_cal()
    print(OpenList.calendarDate)
    OpentimeList = OpenList.isOpen[OpenList.calendarDate == DatetimeNOW]
    print(OpentimeList.values)
    #TODO


# In[13]:


import multiprocessing
from time import sleep
import datetime

# 程序运行时间在上午9:25 到中午 11:30  下午13:30 到 下午 15:00
DAY_START = datetime.time(9,25)
DAY_END = datetime.time(11, 30)

NIGHT_START = datetime.time(13, 30)
NIGHT_END = datetime.time(23, 59)
sell_code = []
code_list = []
message_number = 0
stock_code = list(df.columns)

def run_child():
    while 1:
        print(stock_code)
        sell_stock_df = get_sell_stock(stock_code)
        if sell_stock_df.empty == False:
            message = construct_message_body(sell_stock_df)
            send_message(message)
        for i in list(sell_stock_df.columns):
            stock_code.remove(i)
        sleep(30)

def run_parent():
    print("启动父进程")

    child_process = False  # 是否存在子进程

    while True:
        current_time = datetime.datetime.now().time()

        running = False  # 子进程是否可运行
        if DAY_START <= current_time <= DAY_END or NIGHT_END >= current_time >= NIGHT_START:
            # 判断时候在可运行时
            running = True

        # 在时间段内则开启子进程
        if running and child_process is None:
            print("启动子进程")
            child_process = multiprocessing.Process(target=run_child)
            child_process.start()
            print("子进程启动成功")

        # 非记录时间则退出子进程
        if not running and child_process is not None:
            print("关闭子进程")
            sell_code = []
            child_process.terminate()
            child_process.join()
            child_process = None
            print("子进程关闭成功")

        sleep(5)

if __name__ == '__main__':
    run_parent()


# In[ ]:




