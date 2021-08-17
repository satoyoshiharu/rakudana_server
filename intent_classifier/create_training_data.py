import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import sentencepiece as spm
from gensim.models import Word2Vec, KeyedVectors
import com
import config

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
  tokens = strip_spacemark(tokenizer.EncodeAsPieces(text))
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
  dfname['INTENT'] = intent
  return dfname

if __name__ == '__main__':

  import sys
  import os
  sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
  import config

  DATA_FOLDER = '/media/sf_E_DRIVE/wikipedia'

  sp = spm.SentencePieceProcessor()
  sp.Load("../tokenizer/sentencepiece.model")
  model = KeyedVectors.load('../wordvector/wv.model')

  df_others = pd.read_csv('/media/sf_E_DRIVE/研究社/ej/kej.txt', header=None, sep='\t', names=['SENTENCE'])
  df_others = df_others[df_others['SENTENCE']!='']
  df_others['INTENT'] = com.INTENT_OTHERS

  CORPORA_DIR = '../corpora/intent/'
  CUR_DIR = os.getcwd()
  os.chdir(CORPORA_DIR)

  df_help = gen(com.INTENT_HELP)
  df_yes = gen(com.INTENT_YES)
  df_no = gen(com.INTENT_NO)
  df_cancel = gen(com.INTENT_CANCEL)
  df_retry = gen(com.INTENT_RETRY)
  df_tel = gen(com.INTENT_TEL)
  df_call_police = gen(com.INTENT_CALL_POLICE)
  df_call_emergency = gen(com.INTENT_CALL_EMERGENCY)
  df_send_line_message = gen(com.INTENT_SEND_LINE_MESSAGE)
  df_send_short_message = gen(com.INTENT_SEND_SHORT_MESSAGE)
  df_genkikai = gen(com.INTENT_GENKIKAI)
  df_genkikai_admin = gen(com.INTENT_GENKIKAI_ADMIN)
  df_genkikai_myreservation = gen(com.INTENT_GENKIKAI_MYRESERVATION)
  df_genkikai_news = gen(com.INTENT_GENKIKAI_NEWS)
  df_genkikai_manage_records = gen(com.INTENT_GENKIKAI_MANAGE_RECORDS)
  df_genkikai_manage_reservations = gen(com.INTENT_GENKIKAI_MANAGE_RESERVATIONS)

  os.chdir(CUR_DIR)

  df = pd.concat([df_others,df_help,df_yes,df_no,df_cancel,df_retry,
                  df_tel,df_call_police,df_call_emergency,
                  df_send_line_message,df_send_short_message,
                  df_genkikai, df_genkikai_admin, df_genkikai_myreservation, df_genkikai_news,
                  df_genkikai_manage_records, df_genkikai_manage_reservations])
  print(f"df:{df.shape}")
  labels = df['INTENT'].reset_index()
  labels = labels['INTENT']
  vects = pd.DataFrame([embSum(text, sp, model) for text in df['SENTENCE']])
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
