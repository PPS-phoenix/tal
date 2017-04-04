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

# read spam and ham data. Returns a list of (contents, class) examples
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




       
if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("data_folder")
    args = argparser.parse_args()


    # prepare data
    data = read_data(args.data_folder)
    print(data[0])
    
