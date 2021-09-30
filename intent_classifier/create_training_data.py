import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import sentencepiece as spm
from gensim.models import Word2Vec, KeyedVectors
import com
import config
import MeCab

def strip_spacemark(inputtokenlist):
  # print(inputtokenlist)
  outtokenlist = []
  for t in inputtokenlist:
    t = t.replace('▁', '')
    if t != '':
      outtokenlist.append(t)
  # print(outtokenlist)
  return outtokenlist

def embAvg(text, tokenizer, wvmodel):
  #global model
  #print(f'text: {text}')
  tokens = strip_spacemark(tokenizer.EncodeAsPieces(text))
  #print(f'tokens: {tokens}')
  em = np.array([wvmodel[w] for w in tokens if w in wvmodel])
  if len(em)==0:
    em = np.zeros(config.WORD_VECTOR_SIZE)
  else:
    em = np.mean(em, axis=0)
  #print(f'mean: {em}')
  return em

def embSum(text, tokenizer, wvmodel):
  #global model
  #print(f'text: {text}')
  if config.TOKENIZER == config.SENTENCE_PIECE:
    tokens = strip_spacemark(tokenizer.EncodeAsPieces(text))
  elif config.TOKENIZER == config.MECAB:
    tokens = tokenizer.parse(text).replace('\n','').split(' ')
  #print(f'tokens: {tokens}')
  em = np.array([wvmodel[w] for w in tokens if w in wvmodel])
  if len(em)==0:
    em = np.zeros(config.WORD_VECTOR_SIZE)
  else:
    em = np.sum(em, axis=0)
  #print(f'mean: {em}')
  return em

def gen(intent):
  str = com.intents[intent]
  dfname = pd.read_csv(str + '.txt', header=None, sep='\t', names=['SENTENCE'])
  dfname = dfname[dfname['SENTENCE']!='']
  print(f'gen> {str}')
  dfname['INTENT'] = intent
  return dfname

if __name__ == '__main__':

  import sys
  import os
  sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
  import config

  DATA_FOLDER = '/media/sf_E_DRIVE/wikipedia'

  if config.TOKENIZER == config.SENTENCE_PIECE:
    tokenizer = spm.SentencePieceProcessor()
    tokenizer.Load("../tokenizer/sentencepiece.model")
  elif config.TOKENIZER == config.MECAB:
    tokenizer = MeCab.Tagger(r"-O wakati -d /var/lib/mecab/dic/ipadic-utf8/")

  model = KeyedVectors.load('../wordvector/wv.model')

  df_others = pd.read_csv('/media/sf_E_DRIVE/研究社/ej/kej.txt', header=None, sep='\t', names=['SENTENCE'])
  df_others = df_others[df_others['SENTENCE']!='']
  df_others['INTENT'] = com.INTENT_OTHERS #<--0

  CORPORA_DIR = '../corpora/intent/texts'
  CUR_DIR = os.getcwd()
  os.chdir(CORPORA_DIR)

  print('intent_max::', str(com.INTENT_MAX))
  df_list = [df_others]
  for i in range(1, com.INTENT_MAX+1):
    df_list.append(gen(i))
  print('df list length:', len(df_list))

  os.chdir(CUR_DIR)

  df = pd.concat(df_list)
  print(f"df:{df.shape}")
  labels = df['INTENT'].reset_index()
  labels = labels['INTENT']
  vects = pd.DataFrame([embSum(text, tokenizer, model) for text in df['SENTENCE']])
  print(f'labels:{labels.shape}, vects:{vects.shape}')
  data = pd.concat([labels, vects], axis=1)
  #
  # train,valid,testに分割する。
  #
  train, valid_test = train_test_split(data, train_size=0.8, shuffle=True, stratify=data['INTENT'])
  valid, test = train_test_split(valid_test, test_size=0.5, shuffle=True, stratify=valid_test['INTENT'])
  print(f'train:{train.shape}, valid:{valid.shape}, test:{test.shape}')
  train.iloc[:, :1].to_csv('train.label.txt', sep='\t', index=False, header=False)
  train.iloc[:,1:].to_csv('train.vector.txt', sep='\t', index=False, header=False)
  valid.iloc[:, :1].to_csv('valid.label.txt', sep='\t', index=False, header=False)
  valid.iloc[:,1:].to_csv('valid.vector.txt', sep='\t', index=False, header=False)
  test.iloc[:, :1].to_csv('test.label.txt', sep='\t', index=False, header=False)
  test.iloc[:,1:].to_csv('test.vector.txt', sep='\t', index=False, header=False)
