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


# calcule log p(review|class) + log p(class)
def get_logproba_review_and_class(logprobas_classes, logprobas_words, example, reviewclass):
    logproba = logprobas_classes[reviewclass] # log p(class)

    # add p(word|class) for each word in set of words
    for word in set(example):
        if word in logprobas_words[reviewclass]: logproba += logprobas_words[reviewclass][word]
        else: logproba += logprobas_words[reviewclass]["$UNKNOWN$"]
            
    return logproba


# predict whether an review is good or bad. log p(class|review) is calculated through its bayesian
# reformulation: log p(review|class) + log p(class) - log p(review) log p(review) is the same for
# either class and is therefore omitted in the calculations here because we simply take the highest
# class with the highest log proba, which is unchanged by log p(review).
def predict_review(logprobas_classes, logprobas_words, example):
    
    # calculate scores of each class, representing log p(review|class) + log p(class) for each class
    logproba_bad = get_logproba_review_and_class(logprobas_classes, logprobas_words, example, "bad")
    logproba_good = get_logproba_review_and_class(logprobas_classes, logprobas_words, example, "good")
    
    if logproba_bad > logproba_good: return "bad"
    else: return "good"

        
# predict all emails and return the predicted and gold labels
def predict_all(logprobas_classes, logprobas_words, dev):
    ygolds = []
    ypreds = []
    for example, ygold in dev:
        ypred = predict_review(logprobas_classes, logprobas_words, example)
        ypreds.append(ypred)
        ygolds.append(ygold)
    return ypreds, ygolds


# evaluate prediction and print precision, recall and f-score
def evaluate(ypreds, ygolds):
    assert(len(ypreds)==len(ygolds)) # check equal lengths of predicted and gold
    correct = 0
    for ypred, ygold in zip(ypreds, ygolds):
        if ypred==ygold and ypred=="bad":
            correct += 1
         
    #nombre de prédiction en tant que mauvaise revue
    nb_predicted_bad = len([x for x in ypreds if x=="bad"])
    #nombre réel de mauvaises revues
    nb_gold_bad = len([x for x in ygolds if x=="bad"])

    print ("\n\t\t" + str(correct) + " predictions sur "+ str(nb_predicted_bad) +\
    " sont correctes avec un total de "+ str(nb_gold_bad) +" 'bad review(s)' !\n")
    
    #if correct != 0:
        #on peut delet cette ligne 
    precision = recall = 1
    if nb_predicted_bad != 0:
        precision = correct/float(nb_predicted_bad)
    else:
        print("toutes les revues ont été prédites comme 'good'.")
        precision = 0
    
    if nb_gold_bad != 0:
        recall = correct/float(nb_gold_bad)
    else:
        print("nombre réel de mauvaises revues = null")
        recall = 1
        
    if precision+recall != 0:
        fscore = 2*(precision*recall) / float(precision+recall)
    else:
        print("score = null")
        fscore = 0
        
    
    missShots = nb_predicted_bad-correct
    nbGood = nb_gold_bad-len(ygolds)
    
    erreur = (correct - (nbGood - missShots)) / float(len(ygolds))
        
    print("Precision  \t= "+str(precision*100)+"%")
    print("Exactitude \t= "+str(recall*100)+"%")
    print("Fscore \t= "+str(fscore*100)+"%")
    print("Taux erreur \t= "+str(erreur*100)+"%")

       

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

    # prediction and evaluation on dev set. Adjust the smoothing factor
    # above to get the best possible score on the dev set
    ypreds, ygold = predict_all(logprobas_classes, logprobas_words, dev)
    print("\nScores on dev set: " + '\n' + str(ypreds) + '\n' + str(ygold) )
    evaluate(ypreds, ygold)

    # predict and evaluate on test set (once the smoothing value has been chosen
    ypreds, ygold = predict_all(logprobas_classes, logprobas_words, test)
    print("\nScores on test set: " + '\n' + str(ypreds) + '\n' + str(ygold))
    evaluate(ypreds, ygold)
