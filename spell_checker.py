#Developed from Peter Norvig's tutorial https://github.com/norvig/pytudes/blob/master/ipynb/How%20to%20Do%20Things%20with%20Words.ipynb

import re
import random
import math
from collections import Counter
from matplotlib.pyplot import yscale, xscale, title, plot, show
import string
import glob

alphabet = string.ascii_lowercase

def load_counts(filename, sep='\t'):
    "return a counter initialised from key-value pairs one on each line of filename"
    C=Counter()
    for line in open(filename):
        key, count=line.split(sep)
        C[key]=int(count)
    return C

COUNTS1 = load_counts('data/count_1w.txt')
COUNTS2 = load_counts('data/count_2w.txt')

def pdist(counter):
    "return a probability distribution using evidence from bag of words(counter)"
    N=sum(counter.values())
    return lambda x: counter[x]/N

P1W = pdist(COUNTS1)
P2W = pdist(COUNTS2)

def Pwords2(words,prev='<S>'):
    "the probability of a sequence of words given the previous word, by using bigram data"
    print(words)
    word = re.findall('[a-zA-Z]+',words.lower())
    return product(cPword(word[i],(prev if i==0 else word[i-1])) for i in range(len(word)))

def product(nums):
    "Multiply the numbers together"
    result = 1
    for x in nums:
        result *= x
    return result
#Using the big dictionary with counts of single words
P=P1W

def cPword(word,prev):
    "conditional probability of a word given the word that came before it"
    bigram = prev+' '+word
    if P2W(bigram)>0 and P(word)>0:
        return P2W(bigram)/P(word)
    else:
        return P(word)/2 # Average the back-off value and zero.


def edits1(word):
    "returns all words one edit away from given word"
    pairs = splits(word)
    deletes = [a + b[1:]  for (a,b) in pairs if b]
    inserts = [a + c + b for (a,b) in pairs for c in alphabet if b]
    transposes = [a + b[1] + b[0] + b[2:] for (a,b) in pairs if len(b)>1]
    replaces = [a + c + b[1:] for (a,b) in pairs for c in alphabet]
    return set(deletes + inserts + transposes + replaces)

def splits(word):
    "returns a list of all (first, rest) pairs of the word"
    return [(word[:i],word[i:]) for i in range(len(word)+1)]

def edits2(word):
    "return all strings 2 edits away from the word"
    return {e2 for e1 in edits1(word) for e2 in edits1(e1)}

def edits0(word):
    "return all strings that are 0 edits away from the word, that is the word itself"
    return {word}

def known(words):
    "return the subset of words that are in the dictionary"
    return {w for w in words if w in COUNTS1}

def correct(word):
    "find best spelling correction for this word"
    candidates = (  known(edits0(word))
                 or known(edits1(word))
                 or known(edits2(word))
                 or [word])
    probable_candidates=set()
    for i in range(10):
        if len(candidates)>1:
            temp = max(candidates,key=COUNTS1.get)
            probable_candidates.add(temp)
            candidates.remove(temp)
        else:
            probable_candidates.add(candidates.pop())
            break

    return random.choice(list(probable_candidates))

def case_of(word):
    "return the case-function appropriate for text: upper, lower, title, or just str."
    return (str.upper if word.isupper()
            else str.lower if word.islower()
            else str.title if word.istitle()
            else str)

def correct_match(word):
    "spell-correct word in match, and preserve proper upper/lower/title case."
    word=word.group()
    return case_of(word)(correct(word.lower()))

def correct_text(text):
    "correct all words in a text and return corrected text"
    candidate_text = set()
    for i in range(10):
       candidate_text.add(re.sub('[a-zA-Z]+',correct_match,text))
    return max(candidate_text,key=Pwords2)

text="default"

while text:
    text = input('>')
    corrected_text = correct_text(text)
    print(corrected_text)
