# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 10:34:35 2020

"""
import re
import os
import time
import pandas as pd
import base64
import requests
from PIL import Image

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

for i in range(100):
    text = requests.get('https://www.landchina.com?tabid=263').text
    img_str = re.search('base64,(.+)?"', text).group(1)
    x = base64.urlsafe_b64decode(img_str)
    with open(f'image/img{i + 1}.png', 'wb') as f:
        f.write(x)
    print(i)
    # time.sleep(5 + random.random() * 10)


image_map = {}
filename_list = [filename for filename in os.listdir('image') if not filename.startswith('.')]
for filename in filename_list:
    if filename.startswith('.'):continue
    img = Image.open(f'image/{filename}')
    for i in range(5):
        name = hash(time.time())
        img.crop((i * 20, 0, (i + 1) * 20, 27)).save(f'image_cutted/{name}_{filename[i]}.png')
        image_map[str(name) + f'_{filename[i]}'] = filename[i]
    
image_map = pd.Series(image_map)
image_map = image_map.reset_index()
image_map['index'] = "image_cutted/" + image_map['index'] + '.png'
image_map.to_csv('image_map.txt', columns = None, index = False)
#***************************一些必要的包的调用********************************
import torch.nn.functional as F
import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import Dataset
from PIL import Image
import torch.optim as optim
import os


def default_loader(path):
    return Image.open(path).resize((28, 28)).convert('L')

class MyDataset(Dataset): 
    def __init__(self,txt, transform=None,target_transform=None, loader=default_loader):
        super(MyDataset,self).__init__()
        fh= open(txt, 'r')
        imgs = []
        for line in fh:
            line = line.strip('\n')
            line = line.rstrip('\n')
            words = line.split(',')
            imgs.append((words[0],int(words[1])))

        self.transform = transform
        self.target_transform = target_transform
        self.loader = loader
        self.imgs = imgs        
    
    def __getitem__(self, index):#这个方法是必须要有的，用于按照索引读取每个元素的具体内容
        fn, label = self.imgs[index]
        img = self.loader(fn)
        if self.transform is not None:
            img = self.transform(img)
        return img,label
		                  #return回哪些内容，那么我们在训练时循环读取每个batch时，就能获得哪些内容
		     #**********************************  #使用__len__()初始化一些需要传入的参数及数据集的调用**********************
    def __len__(self):
        return len(self.imgs)
train_data=MyDataset('image_map.txt', transform=transforms.ToTensor())

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
    
n_epochs = 3
batch_size_train = 5
batch_size_test = 1000
learning_rate = 0.01
momentum = 0.5
log_interval = 10
random_seed = 1
torch.manual_seed(random_seed)
network = Net()
optimizer = optim.SGD(network.parameters(), lr=learning_rate,
                      momentum=momentum)

train_loader = torch.utils.data.DataLoader(train_data, batch_size = batch_size_train)

train_losses = []
train_counter = []
test_losses = []
test_counter = [i*len(train_loader.dataset) for i in range(n_epochs + 1)]

def train(epoch):
    network.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        output = network(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))
        train_losses.append(loss.item())
        train_counter.append((batch_idx*64) + ((epoch-1)*len(train_loader.dataset)))
      
for epoch in range(100):
    train(epoch + 1)

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
        

def predict(filename):
    network.train(False)
    image = Image.open(filename)
    imgs = [image.crop((i * 20, 0, (i + 1) * 20, 27)) for i in range(5)]
    test_data=TestDataSet(imgs, transform=transforms.ToTensor())
    test_loader = torch.utils.data.DataLoader(test_data, batch_size = 1)
    predicted_list = []
    for img in test_loader:
        outputs = network(img)
        _, predicted = torch.max(outputs, 1)
        predicted_list.append(int(predicted[0]))
    return ''.join([str(p) for p in predicted_list])
    
predict(f"image_now.png")
image = Image.open(f"image_now.png")
image

torch.save(network, 'model.pkl')

with open(f'image_now.png', 'wb') as f:
        f.write(x)
