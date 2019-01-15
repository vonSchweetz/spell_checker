#Developed from Peter Norvig's tutorial https://github.com/norvig/pytudes/blob/master/ipynb/How%20to%20Do%20Things%20with%20Words.ipynb

import re
import random
import math
from collections import Counter
from matplotlib.pyplot import yscale, xscale, title, plot, show
import string
import glob


alphabet = string.ascii_lowercase
filepath = 'data/gutenberg.txt'
TEXT = open(filepath).read()

def tokens(text):
    words = re.findall('[a-z]+',text.lower())
    return words

WORDS = tokens(TEXT)
COUNTS = Counter(WORDS)

#STANDARD SPELL CHECKER
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
    return {w for w in words if w in COUNTS}

def correct(word):
    "find best spelling correction for this word"
    candidates = (  known(edits0(word))
                 or known(edits1(word))
                 or known(edits2(word))
                 or [word])
    return max(candidates,key=COUNTS.get)

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
    return re.sub('[a-zA-Z]+',correct_match,text)


def pdist(counter):
    "return a probability distribution using evidence from bag of words(counter)"
    N=sum(counter.values())
    return lambda x: counter[x]/N
#
# Pword=pdist(COUNTS)
#
# def Pwords(words):
#     "probability of a sequence of words assuming they are independent"
#     return product(Pword(w) for w in words)
#
def product(nums):
    "Multiply the numbers together"
    result = 1
    for x in nums:
        result *= x
    return result

def memo(f):
    "Memoise function f, whose arguments must all be hashable"
    cache={}
    def fmemo(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    fmemo.cache = cache
    return fmemo
#
# #18
# longest = max(len(w) for w in COUNTS)
#
def splits(text,start=0,L=20):
    return [(text[:i],text[i:]) for i in range(start,min(len(text), L)+1)]

# @memo
# def segment(text):
#     "Return a list of words that is the most probable segmentation of text"
#     if not text:
#         return []
#     else:
#         candidates = ([first] + segment(rest)
#                       for (first, rest) in splits(text, 1))
#         return max(candidates, key=Pwords)
#

def load_counts(filename, sep='\t'):
    "return a counter initialised from key-value pairs one on each line of filename"
    C=Counter()
    for line in open(filename):
        key, count=line.split(sep)
        C[key]=int(count)
    return C

COUNTS1 = load_counts('data/count_1w.txt')
COUNTS2 = load_counts('data/count_2w.txt')

P1W = pdist(COUNTS1)
P2W = pdist(COUNTS2)


def Pwords2(words,prev='<S>'):
    "the probability of a sequence of words given the previous word, by using bigram data"
    return product(cPword(w,(prev if i==0 else words[i-1])) for (i,w) in enumerate(words))

#Using the big dictionary with counts of single words
P=P1W

def cPword(word,prev):
    "conditional probability of a word given the word that came before it"
    bigram = prev+' '+word
    if P2W(bigram)>0 and P(word)>0:
        return P2W(bigram)/P(word)
    else:
        return P(word)/2 # Average the back-off value and zero.

@memo
def segment2(text):
    "return a list of words that is the most probable segmentation of text"
    if not text:
        return []
    else:
        candidates = ([first] + segment2(rest)
                      for (first, rest) in splits(text, 1))
        return max(candidates, key=Pwords2)

# def is_segmented(text):
#     ""

#DO Something to correct this for chatbot
# print(segment("small andinsignificant"))
# def pdist_additive_smoothed(counter, c=1):
#     """the probability of a word, given evidence from counter.
#         add c to the count of each time + unknown item """
#     N = sum(counter.values())
#     Nplus = N + c * (len(counter) + 1)
#     return lambda word: (counter[word] + c) / Nplus
#
# P1w=pdist_additive_smoothed(COUNTS)
#
# singletons = (w for w in COUNTS if COUNTS[w] == 1)
#
# lengths = map(len, singletons)
#
# def pdist_good_turing_hack(counter, onecounter, base=1/26., prior=1e-8):
#     """The probability of word, given evidence from the counter.
#     For unknown words, look at the one-counts from onecounter, based on length.
#     This gets ideas from Good-Turing, but doesn't implement all of it.
#     prior is an additional factor to make unknowns less likely.
#     base is how much we attenuate probability for each letter beyond longest."""
#     N = sum(counter.values())
#     N2 = sum(onecounter.values())
#     lengths = map(len, [w for w in onecounter if onecounter[w] == 1])
#     ones = Counter(lengths)
#     longest = max(ones)
#     return (lambda word:
#             counter[word] / N if (word in counter)
#             else prior * (ones[len(word)] / N2 or
#                           ones[longest] / N2 * base ** (len(word)-longest)))
#
# # Redefine P1w
# P1w = pdist_good_turing_hack(COUNTS1, COUNTS)
#
# # for w in tokens('"The" is most common word in English'):
# #     print(w)
# #     print(Pword(w), w)
#
# # tests = ['this is a test',
# #          'this is a unusual test',
# #          'this is a neverbeforeseen test']
# #
# # for test in tests:
# #     print(Pwords(tokens(test)), test)
text="default"

while text:
    text = input('>')

    Stext = re.findall('[a-z]+',text.lower())
    print(Stext)
    text_to_segment=""
    for s in Stext:
        text_to_segment = text_to_segment+s

    print(text_to_segment)
    # corrected_text = segment2(text)
    # Pcorrected_text = Pwords2(corrected_text)
    # # corrected_text = correct_text(text)
    # # if Pcorrected_text > 0:
    # print(corrected_text,Pcorrected_text)
    # else:
    #     print(text)
