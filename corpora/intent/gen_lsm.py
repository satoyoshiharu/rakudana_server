import random

SEND_INTENT = ['送る','','送信','送信する']
OBJ = ['メッセージ','メッセ']
MODE = ['','','','すぐに','いまから','ちょっと']

if __name__ == "__main__":
    with open('lsm.txt','w') as f:
        for i in range(100):
            f.write(f'{random.choice(MODE)}{random.choice(OBJ)}をLINEで{random.choice(SEND_INTENT)}\n')
            f.write(f'{random.choice(MODE)}LINEで{random.choice(OBJ)}を{random.choice(SEND_INTENT)}\n')
            f.write(f'{random.choice(MODE)}LINE{random.choice(OBJ)}を{random.choice(SEND_INTENT)}\n')
            f.write(f'{random.choice(MODE)}LINE{random.choice(OBJ)}{random.choice(SEND_INTENT)}\n')