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

def test(t):
    print('テスト文:'+t,'=>結果:'+eval(data(t)))

model.eval()
with torch.no_grad():  # batch size is len(dataset_valid)
    test('はい')
    test('いいえ')
    test('キャンセル')
    test('やり直す')

    test('安全診断して')
    test('何ができるか教えて')
    test('電話をかける')
    test('お父さんに電話')
    test('110番に電話')
    test('119番に電話する')
    test('メッセージ送る')
    test('LINE送る')
    test('メモを保存して')
    test('ページをホーム画面に置いて')
    test('コンビニはどこにある')
    test('近くのコンビニはどこ')
    test('ニュースを開いて')
    test('今日の天気')
    test('電卓')

    test('元気かい')
    test('元気かい管理')
    test('元気かい予約確認')
    test('元気かい履歴管理')
    test('元気かい予約管理')



