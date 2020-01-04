# ToDo
# Load the data(Embedded faces)'s location from mongodb -> Done
# Extract face using the location and load them from file system -> Done
# Train the model and then save the model on disk -> Done 

import numpy as np 
import pandas as pd
import os
from os.path import isdir
from numpy import savez_compressed
from os import listdir
from PIL import Image
from numpy import asarray
from numpy import load
from numpy import expand_dims
from keras.models import load_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC
import pickle

# imports for MongoDB
from pymongo import MongoClient
from random import randint
# Imports for AWS S3
from AWS.uploadLocalData import put_object
from AWS.getData import get_embeddings


def getEmbeddings(EMBEDDING_BUCKET_NAME, EmbeddedFaceDataLocation, identity):
	trainX = []
	trainy = []
	location = ''
	temp_location = 'embeddings.npz'
	get_embeddings(EMBEDDING_BUCKET_NAME, EmbeddedFaceDataLocation, location)
	data = load(temp_location)
	trainX, trainy = data['arr_0'], data['arr_1']
	numberOfEnteries = trainX.shape[0]
	trainy = [str(identity) for x in range(numberOfEnteries)]
	trainy = asarray(trainy)
	# Delete file from location after the processing is completed
	data = []
	if os.path.exists(temp_location):
		os.remove(temp_location)
	else:
		print("The file does not exist") 
	return trainX, trainy

def trainData(db,EMBEDDING_BUCKET_NAME):
	print("In trainData")
	trainX = []
	trainy = []
	# Load data(Embedded faces)'s location from mongodb
	collection = db['embeddingCollection']
	cursor = collection.find({},{ 'id': 1,'_id': 0 })
	for document in cursor:
		identity = document['id']
		get = collection.find({'id': identity})
		for locs in get:
			EmbeddedFaceDataLocation = locs['faceEmbeddingDataLocation']
			print("Gathering the embedded data of ", identity, " from ",  EmbeddedFaceDataLocation)

			tempTrainX,tempTrainy = getEmbeddings(EMBEDDING_BUCKET_NAME, EmbeddedFaceDataLocation, identity)
			for allItems in tempTrainX:
				trainX.append(allItems)
			for allItems in tempTrainy:
				trainy.append(allItems)
			
	trainX = asarray(trainX)
	trainy = asarray(trainy)
	print("All embeddings are collected")
	trainX, testX, trainy, testy = train_test_split(trainX, trainy, test_size=0.33, random_state=40)
	print('Dataset: train=%d, test=%d' % (trainX.shape[0], testX.shape[0]))
	print("Train Test split done")
	
	# normalize input vectors
	in_encoder = Normalizer(norm='l2')
	# print(trainX)
	# print(type(trainX))
	trainX = in_encoder.transform(trainX)
	testX = in_encoder.transform(testX)
	print("input vectors normalized")
	
	# label encode targets
	out_encoder = LabelEncoder()
	out_encoder.fit(trainy)
	trainy = out_encoder.transform(trainy)
	testy = out_encoder.transform(testy)
	# Code to update the values of the person in celebFaces collections
	faceIdCollection = db['celebFaces']
	userID = []
	newCursor =  faceIdCollection.find({},{ 'Name': 1,'_id': 0 })
	for enteries in newCursor:
		ID = enteries['Name']
		# print(ID)
		userID.append(ID)
		# myQuery = {"id" : ID}
		# newVal = {"Sr_No" : out_encoder.transform(ID)} 
		# faceIdCollection.update_one(myQuery, newVal)
	print(userID)
	newTestValue = out_encoder.transform(userID)
	print(newTestValue)
	i = 0
	for ID in userID:
		print(ID)
		myQuery = {"Name" : ID}
		newVal = { "$set": {"Sr_No" : str(newTestValue[i])}}
		print("Setting ",str(newTestValue[i]), " for ", ID) 
		faceIdCollection.update_one(myQuery, newVal)
		i += 1;
	
	print("Transformatiom completed")
	
	# fit model
	model = SVC(kernel='linear',probability=True)
	model.fit(trainX, trainy)
	print(model.predict_proba(trainX[0:7]))

	print("Model fitted")
	
	# Saving the Fitted Model
	# save model and architecture to single file
	filename = "Data/SVM_keras_facenet_model_Updated.h5"
	pickle.dump(model, open(filename, 'wb'))

	MODEL_BUCKET = 'iutkarshstudentfacemodel'
	put_object(MODEL_BUCKET, "testSchool01/SVM_model.h5", filename)
	print("Model saved in S3 bucket")
	
	# predict
	yhat_train = model.predict(trainX)
	yhat_test = model.predict(testX)
	
	# score
	score_train = accuracy_score(trainy, yhat_train)
	score_test = accuracy_score(testy, yhat_test)
	
	# summarize
	print('Accuracy: train=%.3f, test=%.3f' % (score_train*100, score_test*100))
	# 	# load the model from disk
	# loaded_model = pickle.load(open(filename, 'rb'))
	# result = loaded_model.score(X_test, Y_test)
	# print(result)


def train(EMBEDDING_BUCKET_NAME):
	print("In train")
	client = MongoClient(port=27017)
	db=client.business
	print("Conncted with the database")
	# printName(db)
	trainData(db,EMBEDDING_BUCKET_NAME)