import MeCab
import re

tagger = MeCab.Tagger(r"-u user.dic")

with open('genkikai_utf8.csv','r') as f:
    line = f.readline()
    while True:
        line = f.readline()
        print(line, end='')
        if line == '': break
        tokens = line.split(',')
        #print(tokens[1],tokens[3])
        parsed = tagger.parse(tokens[1])
        parsed0 = parsed.split('\n')[0]
        attr = re.split('[\t,]', parsed0)
        print(attr)
        if attr[8]!=tokens[3]:
            print(attr[8],'!=',tokens[3])
        #else:
        #    print(attr[8], '==', tokens[3])
        #print(tokens[2],tokens[4])
        parsed = tagger.parse(tokens[2])
        parsed0 = parsed.split('\n')[0]
        attr = re.split('[\t,]', parsed0)
        print(attr)
        if attr[8]!=tokens[4]:
            print(attr[8],'!=',tokens[4])
        #else:
        #    print(attr[8], '==', tokens[3])
f.close()

print(tagger.parse('2月12日午前佐藤好春'))
print(tagger.parse('まさきなおえ'))
print(tagger.parse('あわの'))
