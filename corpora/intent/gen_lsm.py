import random

SEND_INTENT = ['送る','','送信','送信する']
OBJ = ['メッセージ','メッセ']

if __name__ == "__main__":
    with open('../data/lsm.txt','w') as f:
        for i in range(100):
            f.write(f'{random.choice(OBJ)}をLINEで{random.choice(SEND_INTENT)}\n')
            f.write(f'LINEで{random.choice(OBJ)}を{random.choice(SEND_INTENT)}\n')
            f.write(f'LINE{random.choice(OBJ)}を{random.choice(SEND_INTENT)}\n')
            f.write(f'LINE{random.choice(OBJ)}{random.choice(SEND_INTENT)}\n')