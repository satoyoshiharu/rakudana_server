from datetime import datetime


class Entity():
    def __init__(self):
        pass

class Person(Entity):
    def __init__(self, sei='', seiyomi='', mei='', meiyomi='', id='', lineid=''):
        super().__init__()
        self.sei = sei
        self.seiyomi = seiyomi
        self.mei = mei
        self.meiyomi = meiyomi
        self.id = id
        self.lineid = lineid
        self.name = self.seiyomi + self.meiyomi

class Day(Entity):
    def __init__(self,year=None,month=None,day=None,ampm=None,hour=None,minutes=None):
        super().__init__()
        today = datetime.today()
        if year!='':
            self.year = year
        else:
            self.year = today.year
        if month!='':
            self.month = month
        else:
            self.month = today.month
        self.day = day
        self.ampm = ampm
        self.hour = hour
        self.minutes = minutes


class Reservation(Entity):
    def __init__(self):
        super().__init__()
        self.date = None
        self.memberlist = []
        #self.member = Person('','','')


class Visit(Entity):
    def __init__(self):
        super().__init__()
        self.date = None
        self.memberlist = []


class Digits(Entity):
    def __init__(self):
        super().__init__()
        self.value = ''


class NER():

    def __init__(self):
        self.entitylist = []

    def find_entity(self, morphs):
        print('NER.find_entity > ...')
        maxI = len(morphs) - 1
        i = 0
        while True:
            if i > maxI: break
            if 'pos' in morphs[i].keys() and morphs[i]['pos'] == '名詞固有名詞人名姓*':
                pn = Person()
                pn.seiyomi = morphs[i]['base']
                if i<maxI and 'pos' in morphs[i+1].keys() and morphs[i+1]['pos'] == '名詞固有名詞人名名*':
                    pn.meiyomi = morphs[i+1]['base']
                    i += 1
                pn.name = pn.seiyomi + pn.meiyomi
                print(f'NER.find_entity > Person {pn.name}')
                self.entitylist.append(pn)
            elif 'pos' in morphs[i].keys() and morphs[i]['pos'] == '名詞固有名詞人名名*':
                pn = Person()
                pn.meiyomi = morphs[i]['base']
                pn.name = pn.meiyomi
                print(f'NER.find_entity > Person {pn.name}')
                self.entitylist.append(pn)
            elif 'pos' in morphs[i].keys() and morphs[i]['pos'] == '名詞数***':
                # capture 090-2935-5792 or 110
                digit = Digits()
                digit.value = morphs[i]['surface']
                while True:
                    j = i + 1
                    if j < maxI and 'pos' in morphs[j].keys() and morphs[j]['pos'] == '名詞サ変接続***' \
                            and morphs[j]['surface'] == '-':
                        j = j + 1
                        if j < maxI and 'pos' in morphs[j].keys() and morphs[j]['pos'] == '名詞数***':
                            digit.value += morphs[j]['surface']
                            i = j
                    else:
                        break
                print(f'NER.find_entity > Digits {digit.value}')
                self.entitylist.append(digit)
            i += 1
