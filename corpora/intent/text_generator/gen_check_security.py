import random

OBJECTIVE = ['安全','安全度の','安全度のチェック','安全かどうかの']
CHECK_INTENT = ['診断','チェック','診断して','チェックして']
MOOD = ['','','','','えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('../texts/check_security.txt', 'w') as f:
        for i in range(300):
            f.write(f'{random.choice(MOOD)}{random.choice(OBJECTIVE)}{random.choice(CHECK_INTENT)}\n')
