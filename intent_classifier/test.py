import sentencepiece as spm
from gensim.models import KeyedVectors
import torch

import com
import train
import create_training_data
import config
import MeCab

if config.TOKENIZER == config.SENTENCE_PIECE:
    tokenizer = spm.SentencePieceProcessor()
    tokenizer.Load("../tokenizer/sentencepiece.model")
elif config.TOKENIZER == config.MECAB:
    tokenizer = MeCab.Tagger(r"-O wakati -d /var/lib/mecab/dic/ipadic-utf8/")

wv = KeyedVectors.load('../wordvector/wv.model')
print('父', wv.most_similar(positive='父'))
print('人','父', wv.similarity('人','父'))
print('物','父', wv.similarity('物','父'))
print('メッセージ','メモ', wv.similarity('メッセージ','メモ'))
print('送信','保存', wv.similarity('送信','保存'))

szWV = config.WORD_VECTOR_SIZE
numINTENT = com.INTENT_MAX + 1
model = train.Net(szWV, numINTENT)#.to(device)
model.load_state_dict(torch.load('./intent_classifier.model'))

def dump_tokens(str):
    if config.TOKENIZER == config.SENTENCE_PIECE:
        words = create_training_data.strip_spacemark(tokenizer.EncodeAsPieces(str))
        print(" ".join(words))
    elif config.TOKENIZER == config.MECAB:
        print(tokenizer.parse(str).replace('\n', ''))

def data(str):
    dump_tokens(str)
    return torch.tensor(create_training_data.embSum(str, tokenizer, wv), dtype=torch.float)

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
    test('使い方教えて')
    test('電話をかける')
    test('お父さんに電話')
    test('110番に電話')
    test('119番に電話する')
    test('メッセージ送る')
    test('LINE送る')
    test('メモを保存して')
    test('メモを保存したい')
    test('ページをホーム画面に置いて')
    test('ページをホーム画面に置く')
    test('コンビニはどこにある')
    test('近くのコンビニはどこ')
    test('ニュースを開いて')
    test('今日のニュースを出して')
    test('今日の天気')
    test('今日の天気は')
    test('電卓')

    test('元気かい')
    test('元気かい管理')
    test('元気かい予約確認')
    test('元気かい履歴管理')
    test('元気かい予約管理')



