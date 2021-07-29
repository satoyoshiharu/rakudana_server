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

if __name__ == '__main__':

  import sys
  import os
  sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
  import config

  DATA_FOLDER = '/media/sf_E_DRIVE/wikipedia'

  sp = spm.SentencePieceProcessor()
  sp.Load("../tokenizer/sentencepiece.model")

  wv_model = Word2Vec.load('../wordvector/wordvector.model')
  wv_model.wv.save('wv.model')
  model = KeyedVectors.load('wv.model')

  # def wordbreak(s):
  #   word_break = sp.EncodeAsPieces(s)
  #   word_break = strip_spacemark(word_break)
  #   return " ".join(word_break)

  df_others = pd.read_csv('/media/sf_E_DRIVE/研究社/ej/kej.txt', header=None, sep='\t', names=['SENTENCE'])
  df_others = df_others[df_others['SENTENCE']!='']
  df_others['INTENT'] = com.INTENT_OTHERS

  CORPORA_DIR = '../corpora/intent/'
  CUR_DIR = os.getcwd()
  os.chdir(CORPORA_DIR)

  exec(open('gen_help.py').read())
  df_help = pd.read_csv('help.txt', header=None, sep='\t', names=['SENTENCE'])
  df_help = df_help[df_help['SENTENCE']!='']
  df_help['INTENT'] = com.INTENT_HELP

  exec(open('gen_yes.py').read())
  df_yes = pd.read_csv('yes.txt', header=None, sep='\t', names=['SENTENCE'])
  df_yes = df_yes[df_yes['SENTENCE']!='']
  df_yes['INTENT'] = com.INTENT_YES

  exec(open('gen_no.py').read())
  df_no = pd.read_csv('no.txt', header=None, sep='\t', names=['SENTENCE'])
  df_no = df_no[df_no['SENTENCE']!='']
  df_no['INTENT'] = com.INTENT_NO

  exec(open('gen_cancel.py').read())
  df_cancel = pd.read_csv('cancel.txt', header=None, sep='\t', names=['SENTENCE'])
  df_cancel = df_cancel[df_cancel['SENTENCE']!='']
  df_cancel['INTENT'] = com.INTENT_CANCEL

  exec(open('gen_retry.py').read())
  df_retry = pd.read_csv('retry.txt', header=None, sep='\t', names=['SENTENCE'])
  df_retry = df_retry[df_retry['SENTENCE']!='']
  df_retry['INTENT'] = com.INTENT_RETRY

  exec(open('gen_tel.py').read())
  df_tel = pd.read_csv('tel.txt', header=None, sep='\t', names=['SENTENCE'])
  df_tel = df_tel[df_tel['SENTENCE']!='']
  df_tel['INTENT'] = com.INTENT_TEL

  exec(open('gen_police_call.py').read())
  df_call_police = pd.read_csv('call_police.txt', header=None, sep='\t', names=['SENTENCE'])
  df_call_police = df_call_police[df_call_police['SENTENCE']!='']
  df_call_police['INTENT'] = com.INTENT_CALL_POLICE

  exec(open('gen_emergency_call.py').read())
  df_call_emergency = pd.read_csv('call_emergency.txt', header=None, sep='\t', names=['SENTENCE'])
  df_call_emrrgency = df_call_emergency[df_call_emergency['SENTENCE']!='']
  df_call_emergency['INTENT'] = com.INTENT_CALL_EMERGENCY

  exec(open('gen_send_line_message.py').read())
  df_send_line_message = pd.read_csv('send_line_message.txt', header=None, sep='\t', names=['SENTENCE'])
  df_send_line_message = df_send_line_message[df_send_line_message['SENTENCE']!='']
  df_send_line_message['INTENT'] = com.INTENT_SEND_LINE_MESSAGE

  exec(open('gen_send_short_message.py').read())
  df_send_short_message = pd.read_csv('send_short_message.txt', header=None, sep='\t', names=['SENTENCE'])
  df_send_short_message = df_send_short_message[df_send_short_message['SENTENCE']!='']
  df_send_short_message['INTENT'] = com.INTENT_SEND_SHORT_MESSAGE

  os.chdir(CUR_DIR)

  df = pd.concat([df_others,df_help,df_yes,df_no,df_cancel,df_retry,
                  df_tel,df_call_police,df_call_emergency,
                  df_send_line_message,df_send_short_message])
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
