#PROTOCOL = 'http'
PROTOCOL = 'https'
#WS_PROTOCOL = 'ws'
WS_PROTOCOL = 'wss'

CLOUD_INSTANCE = False

VR_STAB_TEST = False

if not CLOUD_INSTANCE:
    HOST_EXTERNAL_IP = '192.168.0.19'
    HOST_INTERNAL_IP = '192.168.0.19'
else:
    HOST_EXTERNAL_IP = 'rakudana.com' #35.199.188.69'
    HOST_INTERNAL_IP = '10.138.0.2'

HOST_PORT = '8080'

LINE_ADMIN_USERID = "U73303fce43ff02051ca356e36998145a"
LINE_ADMIN2_USERID = "Ua3f25b6862be7603f61a2323ca3183fc" #iwata san
LINE_ADMIN3_USERID = "Ufc60e681b482d59d3eeb1a24de4eec10" #murata san
LINE_ADMIN4_USERID = 'U3ebf3bb7d0ad8dac93c52bbddf8d0a3b' #awano san
LINE_CHANNEL_SECRET = "b239e10e3fb6b2166322c22f50c356db"
LINE_CHANNEL_ACCESS_TOKEN = "UAVgoe7Aoq6woQWnEnI02MS7/hLmwM1X+9b4o8IyDlvCcrCeTWE7bRwlvOsy7jcWFmQQ+6PgGX+6rFPWfQ5Bd9kaphbL8e5LHgh6zZgNo+NvKt4PMtOWfqdsxNBvvBsKd8y97tJG0TkQT51hHbdo1wdB04t89/1O/w1cDnyilFU="

WORKING_DIR = '/home/satoyoshiharu/hmc-dialog-server/'

RECVJSON_TIMEOUT = 30 #sec
GC_INTERVAL = 60*15 # garbage collection runs
PROCESS_TIMEOUT = 60*20 # kill process over this elapsed time




