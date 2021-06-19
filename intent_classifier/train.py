
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
import numpy as np
from torch.utils.data import Dataset, DataLoader
import pandas as pd

import config


class IntentDataset(Dataset):
    def __init__(self, x, y):  self.x, self.y = x, y
    def __len__(self):  return len(self.y)
    def __getitem__(self, idx):  return [self.x[idx], self.y[idx]]

class Net(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 64)
        nn.init.kaiming_normal_(self.fc1.weight)
        self.fc2 = nn.Linear(64, output_size)
        nn.init.kaiming_normal_(self.fc2.weight)
        self.bn = nn.BatchNorm1d(64)

    def forward(self, x):
        x = self.fc2(F.relu(self.bn(self.fc1(x))))
        return x

class Measure():
    def __init__(self):
        self.loss_train_list = []
        self.loss_valid_list = []
        self.accuracy_train_list = []
        self.accuracy_valid_list = []

    def init_epoch(self):
        self.correct_train = 0
        self.total_train = 0
        self.correct_valid = 0
        self.total_valid = 0
        self.loss_train = 0.0
        self.loss_valid = 0.0

    def accuracy(self, inputs, outputs, labels):
        total = len(inputs)
        prediction = torch.argmax(outputs, dim=1)
        correct = torch.sum(prediction == labels.squeeze(1))
        return total, correct

    def record_train(self, inputs, outputs, labels, lossitem):
        self.loss_train += lossitem
        total, correct = self.accuracy(inputs, outputs, labels)
        self.total_train += total
        self.correct_train += correct

    def train(self):
        self.loss_train /= len(dataset_train)
        self.accuracy_train = self.correct_train / self.total_train

    def record_valid(self, inputs, outputs, labels, lossitem):
        self.loss_valid += lossitem
        total, correct = self.accuracy(inputs, outputs, labels)
        self.total_valid += total
        self.correct_valid += correct

    def valid(self):
        self.loss_valid /= len(dataset_valid)
        self.accuracy_valid = self.correct_valid / self.total_valid

    def record_epoch(self, epoch):
        print(f'epoch: {epoch + 1}, loss_train: {self.loss_train:.6f}, loss_valid: {self.loss_valid:.6f}, \
    accuracy_train: {self.accuracy_train:.6f}, accuracy_valid: {self.accuracy_valid:.6f}')
        self.loss_train_list.append(self.loss_train)
        self.loss_valid_list.append(self.loss_valid)
        self.accuracy_train_list.append(self.accuracy_train)
        self.accuracy_valid_list.append(self.accuracy_valid)

def draw(numEpochs, loss_train_list, loss_valid_list, accuracy_train_list, accuracy_valid_list):
    plt.ioff()
    plt.figure()
    plt.plot(range(numEpochs), loss_train_list, label='loss_train')
    plt.plot(range(numEpochs), loss_valid_list, label='loss_valid')
    plt.legend()
    plt.xlabel('epoch')
    plt.show()
    plt.savefig('./loss.jpg')
    plt.figure()
    plt.plot(range(numEpochs), accuracy_train_list, label='accuracy_train')
    plt.plot(range(numEpochs), accuracy_valid_list, label='accuracy_valid')
    plt.legend()
    plt.xlabel('epoch')
    plt.show()
    plt.savefig('./accuracy.jpg')

if __name__ == '__main__':
    szWV = 100
    numINTENT = config.INTENT_MAX + 1

    torch.manual_seed(1)
    #device = torch.device('cuda')
    train_batch_size = 64#1024

    numEpochs = 30
    learning_rate = 1.0

    x_train = torch.tensor(pd.read_csv('train.vector.txt', sep='\t', header=None).to_numpy(), dtype=torch.float)
    y_train = torch.tensor(pd.read_csv('train.label.txt', sep='\t', header=None).to_numpy(), dtype=torch.long)
    dataset_train = IntentDataset(x_train, y_train)
    dataloader_train = DataLoader(dataset_train, batch_size=train_batch_size, shuffle=True)
    x_valid = torch.tensor(pd.read_csv('valid.vector.txt', sep='\t', header=None).to_numpy(), dtype=torch.float)
    y_valid = torch.tensor(pd.read_csv('valid.label.txt', sep='\t', header=None).to_numpy(), dtype=torch.long)
    dataset_valid = IntentDataset(x_valid, y_valid)
    dataloader_valid = DataLoader(dataset_valid, batch_size=len(dataset_valid), shuffle=False)

    model = Net(szWV, numINTENT)#.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    measure = Measure()

    for epoch in range(numEpochs):
        measure.init_epoch()

        model.train()
        for batch_index, (inputs, labels) in enumerate(dataloader_train):
            #inputs = inputs.to(device)
            #labels = labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels.squeeze(
                1))  # labels=tensor([[a]]) shape=(1,1) -> labels.squeeze(dim=1)==tensor([a]), shape=(1)
            loss.backward()
            optimizer.step()
            measure.record_train(inputs, outputs, labels, loss.item())
        measure.train()

        model.eval()
        with torch.no_grad():  # batch size is len(dataset_valid)
            inputs, labels = next(iter(dataloader_valid))
            #inputs = inputs.to(device)
            #labels = labels.to(device)
            outputs = model(inputs)
            loss_valid = criterion(outputs, labels.squeeze(
                1))  # labels=tensor([[a],[b],...]) shape=(1334,1) -> labels.squeeze(dim=1)==tensor([a,b...]), shape=(1334)
            measure.record_valid(inputs, outputs, labels, loss_valid.item())
        measure.valid()

        measure.record_epoch(epoch)

    torch.save(model.state_dict(),'./intent_classifier.model')

    draw(numEpochs, measure.loss_train_list, measure.loss_valid_list, measure.accuracy_train_list,measure.accuracy_valid_list)
