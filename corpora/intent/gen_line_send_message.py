import random

SEND_INTENT = ['送る','','送信','送信する']
OBJ = ['メッセージ','メッセ']

if __name__ == "__main__":
    with open('../data/line_send_message.txt','w') as f:
        for i in range(100):
            f.write(f'\n{random.choice(OBJ)}をLINEで{random.choice(SEND_INTENT)}')
            f.write(f'\nLINEで{random.choice(OBJ)}を{random.choice(SEND_INTENT)}')
            f.write(f'\nLINE{random.choice(OBJ)}を{random.choice(SEND_INTENT)}')
            f.write(f'\nLINE{random.choice(OBJ)}{random.choice(SEND_INTENT)}')