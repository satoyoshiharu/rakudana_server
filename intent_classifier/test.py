import sentencepiece as spm
from gensim.models import KeyedVectors
import torch

import com
import train
import create_training_data
import config

sp = spm.SentencePieceProcessor()
sp.Load("../tokenizer/sentencepiece.model")

wv = KeyedVectors.load('../wordvector/wv.model')

szWV = config.WORD_VECTOR_SIZE
numINTENT = com.INTENT_MAX + 1
model = train.Net(szWV, numINTENT)#.to(device)
model.load_state_dict(torch.load('./intent_classifier.model'))

def data(str):
    return torch.tensor(create_training_data.embSum(str, sp, wv), dtype=torch.float)

def eval(t):
    return com.intents[torch.argmax(model(torch.unsqueeze(t,0))).item()]

model.eval()
with torch.no_grad():  # batch size is len(dataset_valid)
    print('はい',eval(data('はい')))
    print('いいえ',eval(data('いいえ')))
    print('キャンセル',eval(data('キャンセル')))
    print('やり直す',eval(data('やり直す')))
    print('電話をかける',eval(data('電話をかける')))
    print('110番に電話',eval(data('110番に電話')))
    print('119番に電話する',eval(data('119番に電話する')))
    print('メッセージ送る',eval(data('メッセージ送る')))
    print('LINE送る',eval(data('LINE送る')))
    print('何ができる？',eval(data('何ができる？')))
    print('お父さんに電話',eval(data('お父さんに電話')))


