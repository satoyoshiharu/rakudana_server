import random

PERSONA = ['あなた','これ']
HELP_INTENT = ['何ができるの','何できる','何ができる','どうすればいいか教えて','何ができるか教えて','何ができるか教えて',
               '何ができるか教えて下さい','何できるか教えて下さい','何ができますか']
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('./help.txt','w') as f:
        for i in range(300):
            f.write(f'{random.choice(HELP_INTENT)}\n')
            f.write(f'{random.choice(PERSONA)}、{random.choice(HELP_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(HELP_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(PERSONA)}、{random.choice(HELP_INTENT)}\n')
