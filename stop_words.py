from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

def stopwrd_removal(string):

    stop_words = []

    for i in set(stopwords.words("english")):
        stop_words.append(i.encode("ascii", "ignore"))
        
    stop_words.append("tell")
    words = word_tokenize(string)
    filtered_sentence = []

    for w in words:
        if w not in stop_words:
            filtered_sentence.append(w)
    
    filtered_sentence = ' '.join(filtered_sentence)
    filtered_sentence = re.sub("[\?\:]+", "", filtered_sentence)
    
    #print("\n" + filtered_sentence)
    
    return filtered_sentence
   
#while 1:
	#input1 = raw_input("Say something: ")
	#stopwrd_removal(input1)
