# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 15:50:07 2020

@author: AXZQ
"""
import time
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def get_list(text):
    soup = BeautifulSoup(text)
    table = soup.find('table', attrs = {'id':'TAB_contentTable'})
    table_rows = table.find_all('tr')
    list_data = []
    for row in table_rows[1:]:
        row_data = pd.Series([ele.text for ele in row.find_all('td')][1:], index = ['行政区', '土地坐落', '总面积', '土地用途', '供应方式', '签定日期'])
        row_data['链接'] = row.find('a').attrs['href']
        list_data.append(row_data)
    return pd.concat(list_data, axis = 1).T

def get_date_str():
    years = list(str(i) for i in range(2016, 2020))
    month_starts = list(f'{i}-1' for i in range(1, 13))
    month_ends = ['1-31', '2-28', '3-31', '4-30', '5-31', '6-30', '7-31', '8-31', '9-30', '10-31', '11-30', '12-31']
    date_strs = []
    for year in years:
        for i in range(12):
            start_date = year + '-' + month_starts[i]
            if i == 1 and year == '2016':
                end_date = '2016-2-29'
            else:
                end_date = year + '-' + month_ends[i]
            date_strs.append((start_date, end_date))
    return date_strs
            
cookies = {'SP.NET_SessionId':'slpyc1jsg3yt23gbrnhtp2cq',
           'security_session_verify':'dcf27a8ae41ce5b163052a6b5f09df97',
           'security_session_high_verify':'6dc15b3a64e420e3eec91254641e9f5f',
           'Hm_lvt_83853859c7247c5b03b527894622d3fa':'1596699805,1596770369',
           'Hm_lpvt_83853859c7247c5b03b527894622d3fa':'1596869897'
          }

session=requests.session()
session.keep_alive = False
session.adapters.DEFAULT_RETRIES = 511

headers = {
    'Host': 'www.landchina.com',
    # 'content-type': 'charset=gb2312',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'https://www.landchina.com?tabid=263',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36 Edg/81.0.416.64',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    # 'Referer': 'https://www.landchina.com/default.aspx?tabid=263',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

url = 'https://www.landchina.com/default.aspx?tabid=263&wmguid=75c72564-ffd9-426a-954b-8ac2df0903b7&p='

def get_simple_date(date):
    return f'{date.year}-{date.month}-{date.day}'

data_list = []
date = pd.to_datetime('2020-08-24')
while date >= pd.to_datetime('2020-07-01'):
    date_before = date - pd.tseries.offsets.Day(4)
    start_date, end_date = get_simple_date(date_before), get_simple_date(date)
    date = date - pd.tseries.offsets.Day(5)
    page_max = 200
    page = 1
    while page <= page_max:
        data = [
        ('__VIEWSTATE', '/wEPDwUJNjkzNzgyNTU4D2QWAmYPZBYIZg9kFgICAQ9kFgJmDxYCHgdWaXNpYmxlaGQCAQ9kFgICAQ8WAh4Fc3R5bGUFIEJBQ0tHUk9VTkQtQ09MT1I6I2YzZjVmNztDT0xPUjo7ZAICD2QWAgIBD2QWAmYPZBYCZg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHgRUZXh0ZWRkAgEPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFhwFDT0xPUjojRDNEM0QzO0JBQ0tHUk9VTkQtQ09MT1I6O0JBQ0tHUk9VTkQtSU1BR0U6dXJsKGh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS9Vc2VyL2RlZmF1bHQvVXBsb2FkL3N5c0ZyYW1lSW1nL3hfdGRzY3dfc3lfamhnZ18wMDAuZ2lmKTseBmhlaWdodAUBMxYCZg9kFgICAQ9kFgJmDw8WAh8CZWRkAgIPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHwJlZGQCAg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfAGgWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAICD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCAgEPZBYCZg8WBB8BBYYBQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjtCQUNLR1JPVU5ELUlNQUdFOnVybChodHRwOi8vd3d3LmxhbmRjaGluYS5jb20vVXNlci9kZWZhdWx0L1VwbG9hZC9zeXNGcmFtZUltZy94X3Rkc2N3X3p5X2pnZ2dfMDEuZ2lmKTsfAwUCNDYWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIBD2QWAmYPZBYCZg9kFgJmD2QWAgIBD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfAGgWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIDD2QWAgIDDxYEHglpbm5lcmh0bWwFiQw8UD48QlI+PC9QPjxUQUJMRT48VEJPRFk+PFRSIGNsYXNzPWZpcnN0Um93PjxURCBzdHlsZT0iQk9SREVSLUJPVFRPTTogMXB4IHNvbGlkOyBCT1JERVItTEVGVDogMXB4IHNvbGlkOyBCT1JERVItVE9QOiAxcHggc29saWQ7IEJPUkRFUi1SSUdIVDogMXB4IHNvbGlkOyBib3JkZXI6MHB4IHNvbGlkIiB2QWxpZ249dG9wIHdpZHRoPTM3MD48UCBzdHlsZT0iVEVYVC1BTElHTjogY2VudGVyIj48QSBocmVmPSJodHRwczovL3d3dy5sYW5kY2hpbmEuY29tLyIgdGFyZ2V0PV9zZWxmPjxJTUcgdGl0bGU9dGRzY3dfbG9nZTEucG5nIGFsdD10ZHNjd19sb2dlMS5wbmcgc3JjPSJodHRwOi8vMjE4LjI0Ni4yMi4xNjYvbmV3bWFuYWdlL3VlZGl0b3IvdXRmOC1uZXQvbmV0L3VwbG9hZC9pbWFnZS8yMDIwMDYxMC82MzcyNzQwNjM0Mjg3NzExMDgxMTExMzEyLnBuZyI+PC9BPjwvUD48L1REPjxURCBzdHlsZT0iQk9SREVSLUJPVFRPTTogMXB4IHNvbGlkOyBCT1JERVItTEVGVDogMXB4IHNvbGlkOyBXT1JELUJSRUFLOiBicmVhay1hbGw7IEJPUkRFUi1UT1A6IDFweCBzb2xpZDsgQk9SREVSLVJJR0hUOiAxcHggc29saWQ7Ym9yZGVyOjBweCBzb2xpZCIgdkFsaWduPXRvcCB3aWR0aD02MjA+PFNQQU4gc3R5bGU9IkZPTlQtRkFNSUxZOiDlrovkvZMsIFNpbVN1bjsgQ09MT1I6IHJnYigyNTUsMjU1LDI1NSk7IEZPTlQtU0laRTogMTJweCI+5Li75Yqe77ya6Ieq54S26LWE5rqQ6YOo5LiN5Yqo5Lqn55m76K6w5Lit5b+D77yI6Ieq54S26LWE5rqQ6YOo5rOV5b6L5LqL5Yqh5Lit5b+D77yJPC9TUEFOPiA8UD48U1BBTiBzdHlsZT0iRk9OVC1GQU1JTFk6IOWui+S9kywgU2ltU3VuOyBDT0xPUjogcmdiKDI1NSwyNTUsMjU1KTsgRk9OVC1TSVpFOiAxMnB4Ij7mjIflr7zljZXkvY3vvJroh6rnhLbotYTmupDpg6joh6rnhLbotYTmupDlvIDlj5HliKnnlKjlj7gmbmJzcDsgJm5ic3A75oqA5pyv5pSv5oyB77ya5rWZ5rGf6Ie75ZaE56eR5oqA6IKh5Lu95pyJ6ZmQ5YWs5Y+4PC9TUEFOPiA8UD48U1BBTiBzdHlsZT0iRk9OVC1GQU1JTFk6IOWui+S9kywgU2ltU3VuOyBDT0xPUjogcmdiKDI1NSwyNTUsMjU1KTsgRk9OVC1TSVpFOiAxMnB4Ij7kuqxJQ1DlpIcxMjAzOTQxNOWPty00Jm5ic3A7ICZuYnNwO+S6rOWFrOe9keWuieWkhzExMDEwMjAwMDY2NigyKSZuYnNwOyAmbmJzcDvpgq7nrrHvvJpsYW5kY2hpbmEyMThAMTYzLmNvbSZuYnNwOyZuYnNwOzxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij52YXIgX2JkaG1Qcm90b2NvbCA9ICgoImh0dHBzOiIgPT0gZG9jdW1lbnQubG9jYXRpb24ucHJvdG9jb2wpID8gIiBodHRwczovLyIgOiAiIGh0dHBzOi8vIik7ZG9jdW1lbnQud3JpdGUodW5lc2NhcGUoIiUzQ3NjcmlwdCBzcmM9JyIgKyBfYmRobVByb3RvY29sICsgImhtLmJhaWR1LmNvbS9oLmpzJTNGODM4NTM4NTljNzI0N2M1YjAzYjUyNzg5NDYyMmQzZmEnIHR5cGU9J3RleHQvamF2YXNjcmlwdCclM0UlM0Mvc2NyaXB0JTNFIikpOzwvc2NyaXB0PjwvU1BBTj4gPC9QPjwvVFI+PC9UQk9EWT48L1RBQkxFPjxQPiZuYnNwOzwvUD4fAQVkQkFDS0dST1VORC1JTUFHRTp1cmwoaHR0cDovL3d3dy5sYW5kY2hpbmEuY29tL1VzZXIvZGVmYXVsdC9VcGxvYWQvc3lzRnJhbWVJbWcveF90ZHNjdzIwMTNfeXdfMS5qcGcpO2RkrsBaKxSd8pgwhCjybKHDG9eoWbuRB2lMjvZEiLZc+Kw='),
        ('__EVENTVALIDATION', '/wEdAALbHK8wRNXzPrXQKSFCBNqxCeA4P5qp+tM6YGffBqgTjfb1mNs3ym7EriuVGhAjNBc1j2dJjhEMQBL3yr0kW6dV'),
        ('hidComName', 'default'),
        ('TAB_QueryConditionItem', '9f2c3acd-0256-4da2-a659-6949c4671a2a'), 
        ('TAB_QuerySortItemList', '282:False'),
        ('TAB_QuerySubmitOrderData', '282:False'),
        ('TAB_QuerySubmitConditionData', f'9f2c3acd-0256-4da2-a659-6949c4671a2a:{start_date}~{end_date}'),
        ('TAB_RowButtonActionControl', ''),
        ('TAB_QuerySubmitPagerData', f'{page}'),
        ('TAB_QuerySubmitSortData', '')]
        while True:
            try:
                text = session.post(url, headers = headers, cookies = cookies, data = data).text
                page_max = int(re.search('共(\d+)?页', text).group(1))
                break
            except:
                time.sleep(5 + random.random() * 10)
        data_list.append(get_list(text))
        print(f'{start_date}到{end_date}时间段内第{page}页的数据提取完成')
        # time.sleep(5 + random.random() * 10)
        page = page + 1
    print(f'--------------------------{start_date}到{end_date}时间段内的数据提取完成-----------------------------------')
    if len(data_list) >= 1000:
        data = pd.concat(data_list)
        data_list = []
        data.to_csv(f'DetailData\{start_date}.csv')