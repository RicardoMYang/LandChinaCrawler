# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 14:58:46 2020

"""
import time
import random
import base64
import re
import requests
import torch
import torch.nn.functional as F
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torch.utils.data import Dataset

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)
    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x)

model = Net()
model.load_state_dict(torch.load('model.pkl'))

# model = torch.load('model.pkl')
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

def test_loader(img):
    return img.resize((28, 28)).convert('L')

class TestDataSet(Dataset):
    def __init__(self, imgs, transform = None, target_transform = None, loader = test_loader):
        self.transform = transform
        self.target_transform = target_transform
        self.loader = loader
        self.imgs = imgs
        
    def __getitem__(self, index):
        img = self.imgs[index]
        img = self.loader(img)
        if self.transform is not None:
            img = self.transform(img)
        return img
    
    def __len__(self):
        return len(self.imgs)

def predict_image(text):
    img_str = re.search('base64,(.+)?"', text).group(1)
    x = base64.urlsafe_b64decode(img_str)
    with open('image_new.png', 'wb') as f:
        f.write(x)
    image = Image.open('image_new.png')
    imgs = [image.crop((i * 20, 0, (i + 1) * 20, 27)) for i in range(5)]
    test_data=TestDataSet(imgs, transform=transforms.ToTensor())
    test_loader = torch.utils.data.DataLoader(test_data, batch_size = 1)
    predicted_list = []
    for img in test_loader:
        outputs = model(img)
        _, predicted = torch.max(outputs, 1)
        predicted_list.append(int(predicted[0]))
    return ''.join([str(p) for p in predicted_list])

def string2hex(s):
    '''将验证码加密'''
    code = ''
    for ch in s:
        code += hex(ord(ch))[2:]
    return code

def get_cookies_session(proxies):
    
    session=requests.session()
    session.keep_alive = False
    session.adapters.DEFAULT_RETRIES = 511
    session.proxies = proxies
    
    while True:
        try:
            cookies = {}
            response1 = session.get('https://www.landchina.com/default.aspx?tabid=386&comname=default&wmguid=75c72564-ffd9-426a-954b-8ac2df0903b7&recorderguid=45d67499-9175-4d92-a776-637cb850d70a', headers = headers)
            cookies['security_session_verify'] = response1.cookies.get('security_session_verify')
            img_code = string2hex(predict_image(response1.text))
            cookies['srcurl'] = string2hex('https://www.landchina.com/default.aspx?tabid=386&comname=default&wmguid=75c72564-ffd9-426a-954b-8ac2df0903b7&recorderguid=45d67499-9175-4d92-a776-637cb850d70a')
            response2 = session.get(f'https://www.landchina.com/default.aspx?tabid=386&comname=default&wmguid=75c72564-ffd9-426a-954b-8ac2df0903b7&recorderguid=45d67499-9175-4d92-a776-637cb850d70a&security_verify_img={img_code}', headers = headers, cookies = cookies)
            cookies['security_session_high_verify'] = response2.cookies.get('security_session_high_verify')
            if cookies['security_session_high_verify'] is None:
                continue
            del cookies['srcurl']
            response3 = session.get('https://www.landchina.com/default.aspx?tabid=386&comname=default&wmguid=75c72564-ffd9-426a-954b-8ac2df0903b7&recorderguid=45d67499-9175-4d92-a776-637cb850d70a', headers = headers, cookies = cookies)
            cookies['ASP.NET_SessionId'] = response3.cookies.get('ASP.NET_SessionId')
            return cookies, session
        except:
            time.sleep(5 + random.random() * 10)
    
