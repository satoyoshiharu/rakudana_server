class Entity():
    def __init__(self):
        pass

class PersonName(Entity):
    def __init__(self):
        self.personName.sei = ''
        self.personName.mei = ''

class DateTime(Entity):
    def __init__(self):
        self.date.year = ''
        self.date.month = ''
        self.date.day = ''
        self.time.hour = ''
        self.time.minute = ''

class NER():

    def __init__(self):
        self.entityList = []

    def findEntity(self, morphs):
        print('NER.findEntity > ...')
        maxI = len(morphs) - 1
        i = 0
        while True:
            if i > maxI: break
            if 'pos' in morphs[i].keys() and morphs[i]['pos'] == '名詞固有名詞人名姓*':
                pn = PersonName()
                pn.sei = morphs[i]['base']
                if i<maxI and 'pos' in morphs[i+1].keys() and morphs[i+1]['pos'] == '名詞固有名詞人名名*':
                    pn.mei = morphs[i+1]['base']
                    i += 1
                self.entityList.append(pn)
            elif 'pos' in morphs[i].keys() and morphs[i]['pos'] == '名詞固有名詞人名名*':
                pn = PersonName()
                pn.mei = morphs[i]['base']
                self.entityList.append(pn)
            i += 1
