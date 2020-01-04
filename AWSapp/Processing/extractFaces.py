# ToDo
# Load the data from mongodb -> Done
# Extract face and save them -> Done
# Save the location on disk and save its location in mongodb face collection -> Done
# Add remove duplicate function
import numpy as np 
import pandas as pd
import os
from os.path import isdir
from numpy import savez_compressed
from os import listdir
from PIL import Image
from numpy import asarray
import mtcnn
from mtcnn.mtcnn import MTCNN

# imports for MongoDB
from pymongo import MongoClient
from random import randint


from AWS.getData import get_image
from AWS.uploadLocalData import put_object

# extract a single face from a given photograph
def extract_face(BUCKET_NAME,S3_FILENAME, required_size=(160, 160)):
	# Download the file and then process
	# load image from file
	# Retrieve the object
	location = ""
	get_image(BUCKET_NAME, S3_FILENAME, location)
	image = Image.open("my_temp_image.jpg")
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

	# Delete file from location -----------------
	if os.path.exists("my_temp_image.jpg"):
		os.remove("my_temp_image.jpg")
	else:
		print("The file does not exist") 
	return face_array

# load images and extract faces for all images in the location
def load_faces(BUCKET_NAME,location,identity):
	faces = list()
	for path in location:
		print(path)
		# print(type(path))
		face = extract_face(BUCKET_NAME,path)
		faces.append(face)
	return faces

def printName(db):
	collection = db['photoCollection']
	 # collection.find({},{ 'id': 1,'location': 0,'_id': 0 }) 
	cursor = collection.find({},{ 'location': 1,'_id': 0 })
	for document in cursor:
		print(document)

def loadLinks(IMAGE_BUCKET_NAME,EXTRACTED_FACE_BUCKET_NAME,db, address):
	# Change the code to save the npz file in s3 insted of local file system
	# Update the code in this function to recognize existing data in faceData.npz
	# Currently the code will delete the existing data(faceData.npz) and reprocess all data
	collection = db['photoCollection']
	 # collection.find({},{ 'id': 1,'location': 0,'_id': 0 }) 
	cursor = collection.find({},{ 'id': 1,'_id': 0 })
	for document in cursor:
		# Print the id of the person
		pathArray = []
		print(document['id'])
		identity = document['id']
		get = db.celebFaces.find({'Name': identity})
		i = 0
		print("responce from mongodb")
		for element in get:
			i+=1
			#print(element)
		print(i)
		data = {'Name':identity}
		
		if i==0:
			print("Inserting for first time")
			result = db.celebFaces.insert_one(data)
			print("Name inserted")
		else:
			print("Name already exists")
			
		get = collection.find({'id': identity})
		for locs in get:
			# Checking whether the faceData.npz file exists
			# if it exists, then do nothing
			# else process data and save the faceData in faceData.npz
			# Change the temp path to point to another bucket 
			temp_path = address + identity + "/faceData.npz"
			# if os.path.isfile(temp_path):
			# 	# File exists
			# 	print("Face data for ",identity," already exists")
			# 	continue

			location = locs['location']
			# print(location)
			print("Finding the face data for ", identity)
			faces = load_faces(IMAGE_BUCKET_NAME,location,identity)
			print("Got faces, now saving in S3 and mongodb")
			# print(faces.shape)
			# Save in directory
			print('>loaded %d examples for class: %s' % (len(faces), identity))
			print(temp_path)
			# try:
			# 	os.mkdir(address + identity)
			# except OSError:
			# 	print("Creation of the directory %s failed" % path)
			# else:
			# 	print("Folder created successfully")
				
			# Save it in local directory and then upload it in s3 bucket
			temp_loc = 'temp.npz'
			savez_compressed(temp_loc, faces, identity)
			# Saving the npz file in S3 bucket
			put_object(EXTRACTED_FACE_BUCKET_NAME, temp_path, temp_loc)
			# Save identity and face data location in mongodb
			# Delete file from location
			if os.path.exists("temp.npz"):
				os.remove("temp.npz")
			else:
				print("The file does not exist")
			data = {
				'id':identity,
				'faceDataLocation': temp_path
			}
			db.faceCollection.insert_one(data)
			print("Insertion successfull for ",identity)
	print("End\n\n")

def loadnewLinks(IMAGE_BUCKET_NAME, EXTRACTED_FACE_BUCKET_NAME, db, address, identity):
	collection = db['photoCollection']
	get = collection.find({'id': identity})
		for locs in get:
			# Checking whether the faceData.npz file exists
			# if it exists, then do nothing
			# else process data and save the faceData in faceData.npz
			# Change the temp path to point to another bucket ---------------------------------
			temp_path = address+ "/"+ identity + "/faceData.npz"
			# if os.path.isfile(temp_path):
			# 	# File exists
			# 	print("Face data for ",identity," already exists")
			# 	continue

			location = locs['location']
			# print(location)
			print("Finding the face data for ", identity)
			faces = load_faces(IMAGE_BUCKET_NAME,location,identity)
			print("Got faces, now saving in S3 and mongodb")
			# print(faces.shape)
			# Save in directory
			print('>loaded %d examples for class: %s' % (len(faces), identity))
			print(temp_path)
			# try:
			# 	os.mkdir(address + identity)
			# except OSError:
			# 	print("Creation of the directory %s failed" % path)
			# else:
			# 	print("Folder created successfully")
				
			# Save it in local directory and then upload it in s3 bucket --------------------------------
			temp_loc = 'temp.npz'
			savez_compressed(temp_loc, faces, identity)
			# Saving the npz file in S3 bucket
			put_object(EXTRACTED_FACE_BUCKET_NAME, temp_path, temp_loc)
			# Save identity and face data location in mongodb
			# Delete file from location -----------------
			if os.path.exists("temp.npz"):
				os.remove("temp.npz")
			else:
				print("The file does not exist")
			data = {
				'id':identity,
				'faceDataLocation': temp_path
			}
			db.faceCollection.insert_one(data)
			print("Insertion successfull for ",identity)
	print("End\n\n")

def save_faces(IMAGE_BUCKET_NAME, EXTRACTED_FACE_BUCKET_NAME):
	print("In save_faces")
	client = MongoClient(port=27017)
	db=client.business
	print("Conncted")
	# printName(db)
	# Add Extracted face bucket name below
	path = "testSchool01/"
	loadLinks(IMAGE_BUCKET_NAME, EXTRACTED_FACE_BUCKET_NAME, db, path)

def save_new_faces(loadnewLinks):
	print("In save_new_faces")
	client = MongoClient(port=27017)
	db=client.business
	print("Conncted")
	# printName(db)
	# Add Extracted face bucket name below
	path = SchoolName
	loadnewLinks(IMAGE_BUCKET_NAME, EXTRACTED_FACE_BUCKET_NAME, db, path, identity)