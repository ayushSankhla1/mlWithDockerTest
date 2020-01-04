# ToDo
# Gather the link/location of the new user's data: Done
# Insert the link/location of the new user's datadata into a collection: Done
# imports for MongoDB
from pymongo import MongoClient
from random import randint
from os import listdir
import os
from os.path import isdir
import numpy as np 
import pandas as pd
from Processing.gatherLink import load_faces 
from Processing.trainModel import train
from Processing.extractFaces import save_faces
from Processing.extractEmbeddings import save_new_embeddings

# load a dataset that contains one subdir for each class that in turn contains images
def load_new_user(db,directory):
	X, y = list(), list()
	foundNewUser = False
	# enumerate folders, on per class
	for subdir in listdir(directory):
		# path
		path = directory + subdir + '/'
		# skip any files that might be in the dir
		if not isdir(path):
		    continue
		# load all faces in the subdirectory
		# print(subdir)
		collection = db['celebFaces']
		query = collection.find({"Name": subdir})
		# Check for new user

		if query.count() == 0:
			foundNewUser = True
			print(subdir, " is not in the database")
			# Now add the user in the celebFace collection
			collection.insert_one( {'Sr_No': "temp", 'Name': subdir } )
			load_faces(db,subdir,path)
			save_faces()
			save_new_embeddings(db,subdir)

		else:
			print(subdir," is in the database")
		# Load if not in the database
	return foundNewUser

def addUser():
	# load train dataset
	print("In addUser")
	client = MongoClient(port=27017)
	db=client.business
	print("Conncted")
	
	# load train dataset location
	foundNewUser = load_new_user(db,'Data/5-celebrity-faces-dataset/train/')
	if foundNewUser:
		# Retrain the model
		print("Added new user(s)")
		train()
		print("Retrained the model")
	# load test dataset location
	# load_dataset_location(db,'Data/5-celebrity-faces-dataset/val/')
	print("New users added")