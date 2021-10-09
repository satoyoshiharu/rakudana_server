import config

if not config.CLOUD_INSTANCE:
    HOST_EXTERNAL_IP = '192.168.0.19'
    HOST_INTERNAL_IP = '192.168.0.19'
else:
    HOST_EXTERNAL_IP = 'rakudana.com' #35.199.188.69'
    HOST_INTERNAL_IP = '10.138.0.2'