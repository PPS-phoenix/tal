# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 16:59:37 2017

@author: manfred
"""

import argparse
import random
import math
import io
import re
import os

# Lecture des données "Good" et "Bad". Retourne une liste d'exemples: (contents, class) 
def read_data(data_folder):
    data = []
    for reviewclass in ["bad", "good"]:
        for filename in os.listdir(data_folder+"/"+reviewclass):
            with io.open(data_folder+"/"+reviewclass+"/"+filename, "r", encoding="utf-8", errors="ignore") as fp:
                contents = tokenise_en(fp.read().replace("\n", " "))
                data.append( (contents, reviewclass) )
    return data

     
def tokenise_en(sent):
    sent = re.sub("([^ ])\'", r"\1 '", sent) # separate apostrophe from preceding word by a space if no space to left
    sent = re.sub(" \'", r" ' ", sent) # separate apostrophe from following word if a space if left

    # separate on punctuation
    cannot_precede = ["M", "Prof", "Sgt", "Lt", "Ltd", "co", "etc", "[A-Z]", "[Ii].e", "[eE].g"] # non-exhaustive list
    regex_cannot_precede = "(?:(?<!"+")(?<!".join(cannot_precede)+"))"
    sent = re.sub(regex_cannot_precede+"([\.\,\;\:\)\(\"\?\!]( |$))", r" \1", sent)
    sent = re.sub("((^| )[\.\?\!]) ([\.\?\!]( |$))", r"\1\2", sent) # then restick several fullstops ... or several ?? or !!
    sent = sent.split() # split on whitespace
    return sent


# Mélange la liste de données
def shuffle_data(data):
    random.shuffle(data)

    
# divise les données en train, dev et test avec une proportion de 70:15:15 
def divide_data(data):
    size = len(data)
    train = data[0:int(size*0.7)]
    dev = data[int(size*0.7)+1:int(size*0.7)+int(size*0.15)+1]
    test = data[int(size*0.7)+int(size*0.15)+2:]
    return train, dev, test


# calcule log p(class) pour chaque class
def calculate_logprobas_classes(train):
    # nombre de chaque classs divisé par le total 
    logpbad = math.log(len([x for x in data if x[1]=="bad"])/float(len(data)))
    logpgood = math.log(len([x for x in data if x[1]=="good"])/float(len(data)))
    return {"bad" : logpbad, "good" : logpgood}



# calcule log p(word|class) pour chaque mot et chaque class
def calculate_logprobas_words(train, smoothing=1):
    class2word2occs = calculate_occs_words(train, smoothing) # get counts

    # calculate log probas
    class2word2logp = {"bad" : {}, "good" : {}}
    for reviewclass in class2word2occs:
        # denominator plus 1*smoothing for unknown word
        denominator = sum([ class2word2occs[reviewclass][w] for w in class2word2occs[reviewclass] ]) + 1*smoothing  
        for word in class2word2occs[reviewclass]:
            class2word2logp[reviewclass][word] = math.log(class2word2occs[reviewclass][word]/float(denominator))

        # add a special token to vocabulary representing all unknown words
        class2word2logp[reviewclass]["$UNKNOWN$"] = math.log((1*smoothing)/float(denominator))
        
    return class2word2logp

# calcule le nombre d'occurrences de chaque mot dans chaque classe
def calculate_occs_words(train, smoothing=1):
    class2word2occs = {"bad" : {}, "good" : {}}
    for example, goldclass in train:
        for word in set(example): 
            if word not in class2word2occs["bad"]:
                class2word2occs["bad"][word] = smoothing
                class2word2occs["good"][word] = smoothing
            class2word2occs[goldclass][word] += 1
    return class2word2occs

       

if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("data_folder")
    args = argparser.parse_args()


    # preparation des données
    data = read_data(args.data_folder)
    
    shuffle_data(data)
    train, dev, test = divide_data(data)

    # entrainement 
    logprobas_classes = calculate_logprobas_classes(train)
    logprobas_words =  calculate_logprobas_words(train, 0.01)


    print(data[0])
