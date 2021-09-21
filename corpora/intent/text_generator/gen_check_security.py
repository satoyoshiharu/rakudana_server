import random

OBJECTIVE = ['安全','安全度の','安全度のチェック','安全かどうかの','使い方の']
CHECK_INTENT = ['診断','チェック','自己診断']
DO_INTENT = ['して','したい','する','やって','やる']
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('../texts/check_security.txt', 'w') as f:
        for i in range(500):
            f.write(f'{random.choice(OBJECTIVE)}{random.choice(CHECK_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(OBJECTIVE)}{random.choice(CHECK_INTENT)}\n')
            f.write(f'{random.choice(OBJECTIVE)}{random.choice(CHECK_INTENT)}{random.choice(DO_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(OBJECTIVE)}{random.choice(CHECK_INTENT)}{random.choice(DO_INTENT)}\n')
