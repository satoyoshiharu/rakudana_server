import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import sentencepiece as spm
from gensim.models import Word2Vec, KeyedVectors

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
    em = np.zeros(100)
  else:
    em = np.mean(em, axis=0)
  #print(f'mean: {em}')
  return em

if __name__ == '__main__':

  import sys
  sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
  import config

  DATA_FOLDER = '/media/sf_E_DRIVE/wikipedia'

  sp = spm.SentencePieceProcessor()
  sp.Load("../corpora/sentencepiece.model")

  wv_model = Word2Vec.load('../corpora/wordvector.model')
  wv_model.wv.save('wv.model')
  model = KeyedVectors.load('wv.model')

  # def wordbreak(s):
  #   word_break = sp.EncodeAsPieces(s)
  #   word_break = strip_spacemark(word_break)
  #   return " ".join(word_break)

  df_others = pd.read_csv('/media/sf_E_DRIVE/研究社/ej/kej.txt', header=None, sep='\t', names=['SENTENCE'])
  df_others = df_others[df_others['SENTENCE']!='']
  df_others['INTENT'] = config.INTENT_OTHERS
  #df_others['SENTENCE'] = df_others['SENTENCE'].map(wordbreak)

  exec(open('../corpora/intent/gen_yes.py').read())
  df_yes = pd.read_csv('yes.txt', header=None, sep='\t', names=['SENTENCE'])
  df_yes = df_yes[df_yes['SENTENCE']!='']
  df_yes['INTENT'] = config.INTENT_YES
  #df_yes['SENTENCE'] = df_yes['SENTENCE'].map(wordbreak)

  exec(open('../corpora/intent/gen_no.py').read())
  df_no = pd.read_csv('no.txt', header=None, sep='\t', names=['SENTENCE'])
  df_no = df_no[df_no['SENTENCE']!='']
  df_no['INTENT'] = config.INTENT_NO
  #df_no['SENTENCE'] = df_no['SENTENCE'].map(wordbreak)

  exec(open('../corpora/intent/gen_tel.py').read())
  df_tel = pd.read_csv('tel.txt', header=None, sep='\t', names=['SENTENCE'])
  df_tel = df_tel[df_tel['SENTENCE']!='']
  df_tel['INTENT'] = config.INTENT_TEL
  #df_tel['SENTENCE'] = df_tel['SENTENCE'].map(wordbreak)

  exec(open('../corpora/intent/gen_lsm.py').read())
  df_sendm = pd.read_csv('lsm.txt', header=None, sep='\t', names=['SENTENCE'])
  df_sendm = df_sendm[df_sendm['SENTENCE']!='']
  df_sendm['INTENT'] = config.INTENT_SENDM
  #df_sendm['SENTENCE'] = df_tel['SENTENCE'].map(wordbreak)


  df = pd.concat([df_others,df_yes,df_no,df_tel,df_sendm])
  print(f"df:{df.shape}")
  labels = df['INTENT'].reset_index()
  labels = labels['INTENT']
  vects = pd.DataFrame([embAvg(text, sp, model) for text in df['SENTENCE']])
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
