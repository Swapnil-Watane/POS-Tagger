import nltk
import pprint
from nltk.corpus import conll2000, conll2002
dicttag = {} # to store tags to number
dictwrd = {} # to store numbering of words
unigram = {} # to store unigram frequencies
dictnum = {} # to store numbers of tags
tag_set = []
wrdtg = nltk.defaultdict(int)
fnm = raw_input("Please enter training data filename:")
print "You entered:", fnm

f = open(fnm, 'r')
nofwds = sum(1 for _ in f)
f.close()

addf = float(1)/float(nofwds)
#print addf
# *********************get the unigrams**************************
# tag = value
print "1. Getting unigrams frequencies."
infile = open(fnm, 'r')
ct = 0
ctnum = 0
while 1:
	line = infile.readline()
	if not line:
		break
	word = line.rstrip().split(None,1)[0].lower()
	tag = line.rstrip().split(None,1)[1]
	if tag in unigram:
		unigram[tag] = unigram[tag] + addf
	else:
		unigram[tag] = addf
		dicttag[tag] = ct
		dictnum[ct] = tag
		tag_set.append(tag)
		ct = ct + 1
	if word not in dictwrd:
		dictwrd[word] = ctnum
		ctnum = ctnum + 1
infile.close()
#for k,v in unigram.iteritems():
#	print k, ' = ', v
tag_set = set(tag_set)


# ***********************get lexical***************************** 
# words x tags matrix
print "2. Getting lexicals frequencies."

infile = open(fnm, 'r')
lexical = [[ 0 for i in range(len(dicttag))] for j in range(len(dictwrd))]
while 1:
	line = infile.readline()
	if not line:
		break
	word = line.rstrip().split(None,1)[0].lower()
	tag = line.rstrip().split(None,1)[1]
	lexical[dictwrd[word]][dicttag[tag]] = lexical[dictwrd[word]][dicttag[tag]] + (float(1)/float(unigram[tag]*nofwds))
	wrdtg[(word,tag)] = wrdtg[(word,tag)] + 1 #(float(1)/float(unigram[tag]*nofwds))
	
import re
def subcat(word):
	if not re.search(r'\w',word):
            return '<PUNCS>'
        elif re.search(r'[A-Z]',word):
            return '<CAPITAL>'
        elif re.search(r'\d',word):
            return '<NUM>'
        elif re.search(r'(ion\b|ty\b|ics\b|ment\b|ence\b|ance\b|ness\b|ist\b|ism\b)',word):
            return '<NOUNLIKE>'
        elif re.search(r'(ate\b|fy\b|ize\b|\ben|\bem)',word):
            return '<VERBLIKE>'
        elif re.search(r'(\bun|\bin|ble\b|ry\b|ish\b|ious\b|ical\b|\bnon)',word):
            return '<JJLIKE>'
        else:
            return '<OTHER>'


new = nltk.defaultdict(int)
for (word,tag) in wrdtg:
	new[(word,tag)] = wrdtg[(word,tag)]
        if wrdtg[(word,tag)] < 5:
		new[(subcat(word),tag)] += wrdtg[(word,tag)]

wrdtg = new
checkwrd = []
for (word,tag) in wrdtg:
	checkwrd.append(word)

infile.close()





# ***********************get bigrams***************************** 
# tags x tags matrix 
print "3. Getting bigrams frequencies."

infile = open(fnm, 'r')
bigrams = [[ 0 for i in range(len(dicttag))] for j in range(len(dicttag))]
line1 = infile.readline()
tag1 = line1.rstrip().split(None,1)[1]

while 1:
	line2 = infile.readline()
	if not line2:
		break
	tag2 = line2.rstrip().split(None,1)[1]
	bigrams[dicttag[tag1]][dicttag[tag2]] = bigrams[dicttag[tag1]][dicttag[tag2]] + (float(1)/float(unigram[tag1]*nofwds))
	tag1 = tag2
infile.close()


# ***********************get trigrams***************************** 
# tag1tag2 x tag3 matrix
print "4. Getting trigrams frequencies."

infile = open(fnm, 'r')
trigrams = [[[ 0 for i in range(len(dicttag))] for j in range(len(dicttag))] for k in range(len(dicttag))]
line1 = infile.readline()
tag1 = line1.rstrip().split(None,1)[1]
line2 = infile.readline()
tag2 = line2.rstrip().split(None,1)[1]

while 1:
	line3 = infile.readline()
	if not line3:
		break
	tag3 = line3.rstrip().split(None,1)[1]
	trigrams[dicttag[tag1]][dicttag[tag2]][dicttag[tag3]] = trigrams[dicttag[tag1]][dicttag[tag2]][dicttag[tag3]] + (float(1)/(float(bigrams[dicttag[tag1]][dicttag[tag2]]*unigram[tag1]*nofwds)))
	#import pdb; pdb.set_trace()
	tag1 = tag2
	tag2 = tag3

infile.close()


#******************************** calculate lambdas ******************************
print "5. Calculating lambdas."
L1 = 0
L2 = 0
L3 = 0
ct = 0
import itertools
for x, y, z in itertools.product(range(len(dicttag)), range(len(dicttag)), range(len(dicttag))):
	if trigrams[x][y][z] > 0:
		tag1 = dictnum[x]
		tag2 = dictnum[y]
		tag3 = dictnum[z]

		xyz = round(float(trigrams[x][y][z])*float(bigrams[dicttag[tag1]][dicttag[tag2]]*unigram[tag1]*nofwds))
		xy = round(float(bigrams[dicttag[tag1]][dicttag[tag2]])*float(unigram[tag1]*nofwds))
		
		yz = round(float(bigrams[dicttag[tag2]][dicttag[tag3]])*float(unigram[tag2]*nofwds))
		yval = round(float(unigram[tag2])*float(nofwds))
		
		zval = round(float(unigram[tag3])*float(nofwds))
		case1 = (float(xyz)-1)/(float(xy)-1) if xy != 1 else 0
		case2 = (float(yz)-1)/(float(yval)-1) if yz != 1 else 0
		case3 = (float(zval)-1)/(float(nofwds)-1) if nofwds != 1 else 0
		res = max(case1,case2,case3)
		L1 = L1 + xyz if res == case1 else L1
		L2 = L2 + xyz if res == case2 else L2
		L3 = L3 + xyz if res == case3 else L3

#print L1, L2, L3
addl = L1+ L2 + L3

#print L1/addl
#print L2/addl
#print L3/addl



#******************************calculate argmax*****************
print "6. Calculating tags"
def get_trigram(tag1, tag2, tag3):
	if tag1 == '*' or tag2 == '*':
		f1 = 0
		f2 = 0
	else:
		f1 = trigrams[dicttag[tag1]][dicttag[tag2]][dicttag[tag3]]
		f2 = bigrams[dicttag[tag2]][dicttag[tag3]]
		
	f3 = float(unigram[tag3])

	return f1 + f2 + f3

def get_wordtag(word, tag):
	if word in checkwrd:
		result = lexical[dictwrd[word]][dicttag[tag]]
		result = float(wrdtg[(word, tag)]) / float(nofwds) 
	else:
		#write  the code for unknown wrds here
		result = float(wrdtg[(subcat(word), tag)]) / float(nofwds) 
	return result

pie = nltk.defaultdict(int)
bckpt = nltk.defaultdict(str)


pie[(-1,'*','*')] = 1
pie[(-2,'*','*')] = 1
fnltag = dict()

sent = "Chancellor of the Exchequer Nigel Lawson's restated commitment to a firm monetary policy has helped to prevent a freefall in sterling over the past week".lower()
#sent = "Yesterday, the United ticket counter was active, with people trying to get flights out, but the airline said demand for seats into the city also was active, with people trying to get there to help family and friends".lower()
#import pdb; pdb.set_trace()
#token = nltk.corpus.conll2000.sents()[6768].lower()
token = nltk.word_tokenize(sent)

for k in range(len(token)):
	for v in tag_set:
		for u in tag_set if k-1 >= 0 else '*':
			result = 0;
			max_tag = '!';
			for w in tag_set if k-2 >= 0 else '*':
				q = get_trigram(w,u,v)
				e = get_wordtag(token[k],v)
				temp =  pie[(k-1,w,u)] * q * e
				
				if temp > result:
					max_tag = w
					result = temp
                       
			pie[(k,u,v)] = result
                	bckpt[(k,u,v)] = max_tag
result = 0
max_v = '!'
max_u = '!'
for u in tag_set:
	for v in tag_set:
		q = get_trigram(u,v,'.')
		temp =  pie[(len(token)-1,u,v)] * q
		if temp > result :
			max_u = u
			max_v = v
		 	result = temp
    
fnltag[len(token)-1] = max_v
fnltag[len(token)-2] = max_u

for i in range(len(token)-3,-1,-1):
	fnltag[i] = bckpt[(i+2,fnltag[i+1],fnltag[i+2])]

print fnltag


