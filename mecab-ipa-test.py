import MeCab
import re

tagger = MeCab.Tagger()
parsed = tagger.parse('2月12日午前佐藤好春')
parsed = tagger.parse('正木直恵')
morphs = []
for token in parsed.split('\n'):
    # attr = token.split('\t')
    attr = re.split('[\t,]', token)
    print(f'getMorphs > attr: {attr}')
    if len(attr) > 8:
        morph = {'surface': attr[0], 'pos': attr[1] + attr[2] + attr[3] + attr[4] + attr[5], 'base': attr[8]}
    elif len(attr) > 1:
        morph = {'surface': attr[0], 'pos': attr[1] + attr[2] + attr[3] + attr[4] + attr[5]}
    else:
        morph = {'surface': attr[0]}
    morphs.append(morph)
print(morphs)