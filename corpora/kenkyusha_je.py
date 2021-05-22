import glob
import re
import codecs

FOLDER = '/media/sf_E_DRIVE/研究社/je'
outf = open(FOLDER+'/kje.txt','w')
for src in glob.glob(FOLDER+"/*.utf8"):
    with open(src, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            sample = re.findall(r'E[KB]/*(.+)$',line)
            if len(sample)>0:
                s = sample[0]
                #print(s)
                s = re.sub(r'[\(\)\<\>「」]+','',s)
                s = s.replace(',','、')
                s = s.replace('.','')
                #print(s)
                s = re.sub(r'\[[^\]\}]+[\]\}]*','',s)
                outf.write(s+'\n')
                #print(s)
outf.close()