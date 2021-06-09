import sentencepiece as spm
from gensim.models import KeyedVectors
import torch
import train
import create_training_data

sp = spm.SentencePieceProcessor()
sp.Load("../corpora/sentencepiece.model")

wv = KeyedVectors.load('wordvectors.model')

szWV = 100
numINTENT = 5
model = train.Net(szWV, numINTENT)#.to(device)
model.load_state_dict(torch.load('./intent_classifier.model'))

input1 = torch.tensor(create_training_data.embAvg('電話する',sp,wv), dtype=torch.float)
input2 = torch.tensor(create_training_data.embAvg('LINEする',sp,wv), dtype=torch.float)
model.eval()
with torch.no_grad():  # batch size is len(dataset_valid)
    print(torch.argmax(model(torch.unsqueeze(input1,0))).item())
    print(torch.argmax(model(torch.unsqueeze(input2,0))).item())

