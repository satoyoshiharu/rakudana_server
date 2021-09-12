import random

SEND_INTENT = ['送る','','送信','送信する','する','して']
OBJ = ['メッセージ','メッセ']
OBJ_MARKER = ['を','']
MODE = ['','','','すぐに','いまから','ちょっと']


if __name__ == "__main__":
    with open('../texts/send_line_message.txt', 'w') as f:
        for i in range(300):
            f.write(f'{random.choice(MODE)}LINE{random.choice(OBJ)}{random.choice(OBJ_MARKER)}{random.choice(SEND_INTENT)}\n')
            f.write(f'{random.choice(MODE)}LINEで{random.choice(OBJ)}{random.choice(OBJ_MARKER)}{random.choice(SEND_INTENT)}\n')
            f.write(f'LINE{random.choice(OBJ)}{random.choice(OBJ_MARKER)}{random.choice(MODE)}{random.choice(SEND_INTENT)}\n')
            f.write(f'LINEで{random.choice(OBJ)}{random.choice(OBJ_MARKER)}{random.choice(MODE)}{random.choice(SEND_INTENT)}\n')
