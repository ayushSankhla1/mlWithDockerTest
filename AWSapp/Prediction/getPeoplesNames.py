import numpy as np 
import pandas as pd
import os
from numpy import asarray
import csv
from numpy import load
from numpy import expand_dims
from numpy import asarray
import scipy.misc

# imports for MongoDB
from pymongo import MongoClient
from random import randint

def getNames(result):
    print("In train")
    client = MongoClient(port=27017)
    db=client.business
    print("Conncted with the database")
    # Load data(Embedded faces)'s location from mongodb
    collection = db['celebFaces']
    names = list()
    print("result type =")
    print(type(result))
    print(result.shape)
    print(result)
    for index in result:
        print("In loop, index=")
        # print(index)
        strIndex = str(index)
        print(strIndex)
        get = collection.find({ "Sr_No": strIndex })
        for name in get:
            tempName = name['Name']
            print("Got ",tempName)
            names.append(tempName)
    return names