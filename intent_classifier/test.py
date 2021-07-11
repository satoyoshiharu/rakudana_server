import sentencepiece as spm
from gensim.models import KeyedVectors
import torch

import com
import train
import create_training_data

sp = spm.SentencePieceProcessor()
sp.Load("../tokenizer/sentencepiece.model")

wv = KeyedVectors.load('wv.model')

szWV = 100
numINTENT = com.INTENT_MAX + 1
model = train.Net(szWV, numINTENT)#.to(device)
model.load_state_dict(torch.load('./intent_classifier.model'))

input1 = torch.tensor(create_training_data.embAvg('電話をかける',sp,wv), dtype=torch.float)
input1_1 = torch.tensor(create_training_data.embAvg('電話かける',sp,wv), dtype=torch.float)
input2 = torch.tensor(create_training_data.embAvg('LINEする',sp,wv), dtype=torch.float)
input3 = torch.tensor(create_training_data.embAvg('メッセージ送る',sp,wv), dtype=torch.float)
input4 = torch.tensor(create_training_data.embAvg('何ができますか',sp,wv), dtype=torch.float)
model.eval()
with torch.no_grad():  # batch size is len(dataset_valid)
    print(com.intents[torch.argmax(model(torch.unsqueeze(input1,0))).item()])
    print(com.intents[torch.argmax(model(torch.unsqueeze(input1_1,0))).item()])
    print(com.intents[torch.argmax(model(torch.unsqueeze(input2,0))).item()])
    print(com.intents[torch.argmax(model(torch.unsqueeze(input3,0))).item()])
    print(com.intents[torch.argmax(model(torch.unsqueeze(input4,0))).item()])

