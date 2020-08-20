# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 17:38:19 2020

"""

import time
import random

import pandas as pd
from bs4 import BeautifulSoup

def get_data(text):
    soup = BeautifulSoup(text)
    table = soup.find('table', attrs = {'class':'theme'})
    trs = table.tbody.find_all('tr', recursive=False)
    info_dict = {}
    info_dict['行政区'] = trs[2].find_all('td')[1].text.strip()
    info_dict['电子监管号'] = trs[2].find_all('td')[-1].text.strip()
    info_dict['项目名称'] = trs[3].find_all('td')[-1].text.strip()
    info_dict['项目位置'] = trs[4].find_all('td')[-1].text.strip()
    info_dict['面积(公顷)'] = float(trs[5].find_all('td')[1].text.strip()) if trs[5].find_all('td')[1].text.strip() != '' else ''
    info_dict['土地来源'] = float(trs[5].find_all('td')[-1].text.strip()) if trs[5].find_all('td')[-1].text.strip() != '' else ''
    if info_dict['土地来源'] == 0:
        info_dict['土地来源'] = "新增建设用地"
    elif info_dict['面积(公顷)'] == info_dict['土地来源']:
        info_dict['土地来源'] = "现有建设用地"
    else:
        info_dict['土地来源'] = '新增建设用地(来自存量库)'
    info_dict['土地用途'] = trs[6].find_all('td')[1].text.strip()
    info_dict['供地方式'] = trs[6].find_all('td')[-1].text.strip()
    info_dict['土地使用年限'] = trs[7].find_all('td')[1].text.strip()
    info_dict['行业分类'] = trs[7].find_all('td')[-1].text.strip()
    info_dict['土地级别:'] = trs[8].find_all('td')[1].text.strip()
    info_dict['成交价格(万元)'] = trs[8].find_all('td')[-1].text.strip()
    info_dict['分期支付约定(万元)'] = [td.text.strip() for td in trs[9].find_all('td')[1].find_all('td') if td.text.strip() != ''][7:]
    info_dict['分期支付约定(万元)'] = '-'.join(info_dict['分期支付约定(万元)'])
    info_dict['土地使用权人'] = trs[10].find_all('td')[-1].text.strip()
    info_dict['约定容积率下限'] = trs[12].find('table').find_all('td')[-3].text.strip()
    info_dict['约定容积率上限'] = trs[12].find('table').find_all('td')[-1].text.strip()
    info_dict['约定交地时间'] = trs[12].find_all('td')[-1].text.strip()
    info_dict['约定开工时间'] = trs[13].find_all('td')[-3].text.strip()
    info_dict['约定竣工时间'] = trs[13].find_all('td')[-1].text.strip()
    info_dict['实际开工时间'] = trs[14].find_all('td')[-3].text.strip()
    info_dict['实际竣工时间'] = trs[14].find_all('td')[-1].text.strip()
    info_dict['批准单位'] = trs[15].find_all('td')[1].text.strip()
    info_dict['合同签订日期'] = trs[15].find_all('td')[-1].text.strip()
    return pd.Series(info_dict)

headers = {
    'Host': 'www.landchina.com',
    # 'content-type': 'charset=utf8',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'https://www.landchina.com?tabid=263',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36 Edg/81.0.416.64',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.landchina.com/default.aspx?tabid=263',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

from proxies import ProxyCrawler
p = ProxyCrawler()

def get_proxies(n = 20):
    proxies = p.get_proxies(n)
    proxy_list = []
    for proxy in proxies['proxy']:
        proxy_list.append({'http':'http://' + proxy, 'https':'https://' + proxy})
    return proxy_list

import threading
import os
from LogHandler import LogHandler
from GetCookies import get_cookies_session
from queue import Queue, Empty

used_link_file_names = set()

def get_detail_links(filename):
    link_data = pd.read_csv(f'DetailData/{filename}')
    return link_data['链接'][link_data['供应方式'].isin(['挂牌出让', '拍卖出让', '招标出让'])].to_list()

class GetDetails(threading.Thread):
    
    def __init__(self, link_queue, data_queue, thread_name, proxies):
        threading.Thread.__init__(self, name = thread_name)
        self.log = LogHandler('detail_data_crawler')
        self.link_queue = link_queue
        self.data_queue = data_queue
        self.proxies = proxies
        
    def run(self):
        cookies, session = get_cookies_session(self.proxies)
        while True:
            try:
                url = self.link_queue.get(block = False)
            except Empty:
                self.log.info(f"{self.name}的线程因队列为空退出")
                break
            
            
            try:
                full_url = 'http://www.landchina.com/' + url
                text = self.session.get(full_url).text
                data = get_data(text)
                data['链接'] = url
                self.data_queue.put(data)
                self.log.info(f'{self.name}的线程成功获取{url}的数据')
                time.sleep(5 + random.random() * 10)
            except:
                self.log.info(f'代理失效，{self.name}的线程退出')

while True:
    detail_links = get_detail_links()
    link_queue = Queue()
    for link in detail_links:
        link_queue.put(link)
    data_queue = Queue()
    while not link_queue.empty():
        proxies_list = get_proxies()
        thread_list = []
        for proxy in proxies_list:
            thread_list.append(GetDetails(link_queue, data_queue, proxy, proxy))
        
        for t in thread_list:
            t.start()
        
        for t in thread_list:
            t.join()

link_file_names = [filename for filename in os.listdir('DetailData') if not filename.startswith('.')]
link_file_names = list(reversed(link_file_names))[1:]
unsuccess_list = []
def get_data_without_proxy():
    cookies, session = get_cookies_session(None)
    for filename in link_file_names:
        data_list = []
        detail_links = get_detail_links(filename)
        for i in range(len(detail_links)):
            link = detail_links[i]
            full_url = 'http://www.landchina.com/' + link if filename != '2020-4-1.csv' else link
            while True:
                count = 0
                try:
                    text = session.get(full_url, headers = headers, cookies = cookies, timeout = 10).text
                    data = get_data(text)
                    data['链接'] = full_url
                    data_list.append(data)
                    break
                except:
                    print('没有获取到数据, 正在重新尝试.........')
                    count += 1
                    if count == 5:
                        unsuccess_list.append(link)
                        break
                    cookies, session = get_cookies_session(None)
                    time.sleep(5 + random.random() * 10)
            print(i)
            if i % 100 == 99:
                print(f'第{i + 1}个链接的数据提取完成！')
        detail_data_all = pd.concat(data_list, axis = 1).T
        detail_data_all.to_csv(f'{filename[:-4]}详细数据.csv')
                    
        
