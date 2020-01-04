# ToDo
# Load the data(identity) from mongodb -> Done
# Extract face using the identity and load them from file system -> Done
# Calculate the embeddings and save them on disk and save the location on mongodb -> Done

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

# imports for MongoDB
from pymongo import MongoClient
from random import randint

# Imports for AWS S3
from AWS.uploadLocalData import put_object
from AWS.getData import get_extracted_faces


# get the face embedding for one face
def get_embedding(model, face_pixels):
	# scale pixel values
	face_pixels = face_pixels.astype('float32')
	# standardize pixel values across channels (global)
	mean, std = face_pixels.mean(), face_pixels.std()
	face_pixels = (face_pixels - mean) / std
	# transform face into one sample
	samples = expand_dims(face_pixels, axis=0)
	# make prediction to get embedding
	yhat = model.predict(samples)
	return yhat[0]

def convertToEmbeddings(embeddingModel, identity,BUCKET_NAME, S3_FILENAME):
	location = ''
	get_extracted_faces(BUCKET_NAME, S3_FILENAME, location)

	data = load(location+'faceData.npz')
	faceData = data['arr_0']
	print('faceData Loaded: ', faceData.shape)
	# convert each face in the train set to an embedding
	embeddedface = list()
	for face_pixels in faceData:
		embedding = get_embedding(embeddingModel, face_pixels)
		embeddedface.append(embedding)
	embeddedface = asarray(embeddedface)
	print(embeddedface.shape)
	data = []
	# Delete file from location after the processing is completed
	if os.path.exists("faceData.npz"):
		os.remove("faceData.npz")
	else:
		print("The file does not exist") 
	return embeddedface

def process_new_faces(db, embeddingModel, EXTRACTED_FACE_BUCKET_NAME, EMBEDDING_BUCKET_NAME, pathToEmbedding, identity):
	# Update to use S3
	collection = db['faceCollection']
	get = collection.find({'id': identity})
	for locs in get:
			faceDataLocation = locs['faceDataLocation']
			print("Converting the face data of ", identity)
			print(faceDataLocation)
			embeddedface = convertToEmbeddings(embeddingModel, identity, EXTRACTED_FACE_BUCKET_NAME, faceDataLocation)
			temp_path = pathToEmbedding + identity + "/embeddingsData.npz"
			print(temp_path)
			# Save identity and face data location in mongodb
			data = {
				'id':identity,
				'faceEmbeddingDataLocation': temp_path
			}
			db.embeddingCollection.insert_one(data)
			temp_loc = 'tempEmbeddingsData.npz'
			savez_compressed(temp_path, embeddedface, identity)
			put_object(EMBEDDING_BUCKET_NAME, temp_path, temp_loc)
			print("Embedding for ", identity, " Completed and saved in MongoDb and S3 Bucket")
			print("Insertion successfull for ",identity)
			# Delete file from location -----------------
			if os.path.exists(temp_loc):
				os.remove(temp_loc)
			else:
				print("The file does not exist")

def processFaces(db, embeddingModel, EXTRACTED_FACE_BUCKET_NAME, EMBEDDING_BUCKET_NAME, pathToEmbedding):
	collection = db['faceCollection']
	cursor = collection.find({},{ 'id': 1,'_id': 0 })
	for document in cursor:
		identity = document['id']
		get = collection.find({'id': identity})
		for locs in get:
			faceDataLocation = locs['faceDataLocation']
			print("Converting the face data of ", identity)
			print(faceDataLocation)
			embeddedface = convertToEmbeddings(embeddingModel, identity, EXTRACTED_FACE_BUCKET_NAME, faceDataLocation)
			# Code to save it in Local file system
			temp_path = pathToEmbedding + identity + "/embeddingsData.npz"
			print(temp_path)
			# Save identity and face data location in mongodb
			data = {
				'id':identity,
				'faceEmbeddingDataLocation': temp_path
			}
			db.embeddingCollection.insert_one(data)
			print("Insertion successfull for ",identity)
			temp_loc = 'tempEmbeddingsData.npz'
			savez_compressed(temp_loc, embeddedface, identity)
			# Saving the npz file in S3 bucket
			# Save identity and face data location in mongodb
			# data = {
			# 	'id':identity,
			# 	'faceDataLocation': temp_path
			# }
			# db.faceCollection.insert_one(data)
			# print("Insertion successfull for ",identity)
			put_object(EMBEDDING_BUCKET_NAME, temp_path, temp_loc)
			print("Embedding for ", identity, " Completed and saved in MongoDb, and uploaded to AWS S3 Bucket")
			# Delete file from location -----------------
			if os.path.exists(temp_loc):
				os.remove(temp_loc)
			else:
				print("The file does not exist")

			

def save_embeddings(EXTRACTED_FACE_BUCKET_NAME,EMBEDDING_BUCKET_NAME):
	print("In save_embeddings")
	client = MongoClient(port=27017)
	db=client.business
	print("Conncted with the database")
	# printName(db)
	print("Loading Model")
	embeddingModel = load_model('Data/facenet_keras.h5')
	print("Model loaded")
	pathToEmbedding = "testSchool01/"
	processFaces(db,embeddingModel, EXTRACTED_FACE_BUCKET_NAME, EMBEDDING_BUCKET_NAME, pathToEmbedding)

def save_new_embeddings(EXTRACTED_FACE_BUCKET_NAME,EMBEDDING_BUCKET_NAME, SchoolName, identity):
	# Connecting with MongoDB
	client = MongoClient(port=27017)
	db=client.business
	print("Conncted with the database")
	# Update to use S3
	print("Loading Model")
	embeddingModel = load_model('Data/facenet_keras.h5')
	print("Model loaded")
	pathToEmbedding = SchoolName
	process_new_faces(db, embeddingModel, EXTRACTED_FACE_BUCKET_NAME, EMBEDDING_BUCKET_NAME, pathToEmbedding, identity)
