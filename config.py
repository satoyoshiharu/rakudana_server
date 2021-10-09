#CLOUD_INSTANCE = True
CLOUD_INSTANCE = False

#PROTOCOL = 'http'
PROTOCOL = 'https'
#WS_PROTOCOL = 'ws'
WS_PROTOCOL = 'wss'

VR_STAB_TEST = False
#VR_STAB_TEST = True

if not CLOUD_INSTANCE:
    HOST_EXTERNAL_IP = '192.168.0.19'
    HOST_INTERNAL_IP = '192.168.0.19'
else:
    HOST_EXTERNAL_IP = 'rakudana.com' #35.199.188.69'
    HOST_INTERNAL_IP = '10.138.0.2'

HOST_PORT = '8080'

WORKING_DIR = '/home/satoyoshiharu/hmc-dialog-server/'

RECVJSON_TIMEOUT = 30 #sec
GC_INTERVAL = 60*15 # garbage collection runs
PROCESS_TIMEOUT = 60*20 # kill process over this elapsed time

WORD_VECTOR_SIZE = 128 # 64

SENTENCE_PIECE = 1
MECAB = 0
TOKENIZER = MECAB




