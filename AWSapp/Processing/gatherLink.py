# ToDo
# Gather the link/location of the data: Done
# Insert the link/location of the data into a collection: Done

import numpy as np 
import pandas as pd
import os
from os.path import isdir
from numpy import savez_compressed
from os import listdir
from PIL import Image
from numpy import asarray
from mtcnn.mtcnn import MTCNN

# imports for MongoDB
from pymongo import MongoClient
from random import randint


def printLoc():
	# print the location
	location = "Data/5-celebrity-faces-dataset"

	for dirname, _, filenames in os.walk(location):
		for filename in filenames:
			print(os.path.join(dirname, filename))

# extract a single face from a given photograph
def extract_face(filename, required_size=(160, 160)):
    # load image from file
    image = Image.open(filename)
    # convert to RGB, if needed
    image = image.convert('RGB')
    # convert to array
    pixels = asarray(image)
    # create the detector, using default weights
    detector = MTCNN()
    # detect faces in the image
    results = detector.detect_faces(pixels)
    # extract the bounding box from the first face
    x1, y1, width, height = results[0]['box']
    # bug fix
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    # extract the face
    face = pixels[y1:y2, x1:x2]
    # resize pixels to the model size
    image = Image.fromarray(face)
    image = image.resize(required_size)
    face_array = asarray(image)
    return face_array

def update_location(db,id, new_loc):
	for eachPath in new_loc:
	    db.photoCollection.update({'id': id}, {'$push': {'location': eachPath}})


# load images and extract faces for all images in a directory
def load_faces(db,subdir,directory):
	# faces = list()
	pathArray = []
	# enumerate files
	print("Name of the images of ")
	print(subdir)
	get = db.celebFaces.find({'Name': subdir})
	i = 0
	print("responce from mongodb")
	for element in get:
		i+=1
		#print(element)
	print(i)
	data = {'Name':subdir}
	
	if i==0:
		print("Inserting for first time")
		result = db.celebFaces.insert_one(data)
		print("Name inserted")
	else:
		print("Name already exists")

	for filename in listdir(directory):
		# path
		path = directory + filename
		# get face
		print(path)
		pathArray.append(path)

		# face = extract_face(path)
		# # store
		# faces.append(face)
	
	get = db.photoCollection.find({'id': subdir})
	i = 0
	print("responce from mongodb")
	for element in get:
		i+=1
		#print(element)
	print(i)
	data = {'id':subdir,
			'location': pathArray
	}
	
	if i==0:
		result = db.photoCollection.insert_one(data)
		print("Inserting for first time")
	else:
		print("Updating data")
		update_location(db,subdir,pathArray)
	print("Data inserted")
	# return faces

# load a dataset that contains one subdir for each class that in turn contains images
def load_dataset_location(db,directory):
	X, y = list(), list()
	# enumerate folders, on per class
	for subdir in listdir(directory):
		# path
		path = directory + subdir + '/'
		# skip any files that might be in the dir
		if not isdir(path):
		    continue
		# load all faces in the subdirectory
		load_faces(db,subdir,path)
		print(subdir)

def loadData():
	# load train dataset
	client = MongoClient(port=27017)
	db=client.business
	print("Conncted")
	
	# load train dataset location
	load_dataset_location(db,'Data/5-celebrity-faces-dataset/train/')
	# load test dataset location
	load_dataset_location(db,'Data/5-celebrity-faces-dataset/val/')
	print("database location completed")