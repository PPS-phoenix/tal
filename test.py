# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 23:53:11 2017

@author: manfred
"""

from reviewAnalyser import *

def start():
    print("\n\t\t\t*** Binvenue dans i-Opinion ou Opinion Way ***\n"+
    "\tLe logiciel d'analyse et de classification des revues cinématographiques !\n")
    

def end():
    print("\n\t\t\t*** Opinion Way vous remercie de votre viste, à bientôt ! ***\n")
    
    
def menu():
    print("Choisissez une méthode d'entrainement parmi les suivantes:"+
          "\n\t1. Analyse par sac de mots"+
          "\n\t2. Analyse des négations (non implémentée)")
    
    repCorrecte = False
                
    while repCorrecte == False:
        methode = raw_input("\nEntrez le numéro de la méthode choisie : "+
                            "(q pour quitter) \n>> ")
        
        if(methode == "1"):
            apprentissageSac2Mot()
            eprouverApprentissage()
            
            
        elif(methode == "q"):
            repCorrecte = True
 
        else:
            print("Cette méthode n'est pas encore implémentée !")
        

def eprouverApprentissage():
    test = []
    
    repCorrecte = False
    while repCorrecte == False:
        rep = raw_input("\nVoulez-vous éprouver l'aprentissage du logiciel en"+
        " rentrant vos propres reviews ? (o/n)\n>> ")
        
        if(rep == "o" or rep == "oui" or rep == "y" or rep == "yes"):
           entrerReview(test)
            
        elif(rep == "n" or rep == "non" or rep == "no" or rep == "No"):
            print("retour menu !")
            repCorrecte = True
        
        else:
            print("Votre réponse est incorrecte !")


# Teste si un string s est une suite de chiffre on non.
def isInt(s):
    if not s or (s.startswith('0') and len(s) > 1):
        return False
        
    for c in s:
        if c not in '0123456789':
            return False
        
    return True


def entrerReview(test):
    review = raw_input("Veuillez retrer votre critique : ")
    
    repCorrecte = False
    while repCorrecte == False:
        note = raw_input("Veuillez noter votre critique de 1 à 5 : \n>> ")
        
        if isInt(note) :
            note = int(note)
            
            if note >= 0 and note <= 5 :
                repCorrecte = True
            
        else:
            print("Votre réponse est incorrecte !")
    
    #ajout de la critique dans la BDD
    if(note >2):
        label = "good"
    else:
        label = "bad"
    
    contents = tokenise_en(review.replace("\n", " "))
    test.append( (contents, label) )  
    print (test[0])
    
    fichier = open("data.txt", "a")
    fichier.write("Bonjour monde")
    fichier.close()
    
    data = []
    for reviewclass in ["bad", "good"]:
        for filename in os.listdir(data_folder+"/"+label):
            with io.open(data_folder+"/"+label+"/"+filename, "r", encoding="utf-8", errors="ignore") as fp:
                contents = tokenise_en(fp.read().replace("\n", " "))
                data.append( (contents, label) )
    
def f():
    # entrainement 
    logprobas_classes = calculate_logprobas_classes(train)
    logprobas_words =  calculate_logprobas_words(train, 0.01)
    
    #analyse de la critique
    ypreds, ygold = predict_all(logprobas_classes, logprobas_words, test)
    print("\nScores on dev set: " + '\n' + str(ypreds) + '\n' + str(ygold) )
    evaluate(ypreds, ygold)
       
    #Le programme l'analysera et affichera sa prédiction.")    


if __name__=="__main__":
    start()
    menu()
    end()
    
  
    #Test en retrant des phrases et on voit la réponse du bot
    #ajouter des phrases, les tester, aprouver la prédiction et enregistrer le 
    #fichier txt dans le dossier adéquat
    #traitement des critiques + élaboration de graphe se lon le film ?
    
    #Affiner l'échelle  de classification des reviews : notation
    #Identifier automatiquement certains aspects des reviews qui peuvent être pertinents")
