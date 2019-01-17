alphabet = string.ascii_lowercase
filepath = 'data/gutenberg.txt'
TEXT = open(filepath).read()


def tokens(text):
    words = re.findall('[a-z]+',text.lower())
    return words

WORDS = tokens(TEXT)
COUNTS = Counter(WORDS)

data = open("data/count_1w.txt",'w')
for i in COUNTS:
    data.write(i+'\t'+str(COUNTS[i])+'\n')
