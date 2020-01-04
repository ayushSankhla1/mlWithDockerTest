import numpy as np 
import pandas as pd
import os
import mtcnn
from PIL import Image
from numpy import asarray
from mtcnn.mtcnn import MTCNN
import csv
from os.path import isdir
from numpy import savez_compressed
from os import listdir
from matplotlib import pyplot
from numpy import load
from numpy import expand_dims
from numpy import asarray
from numpy import savez_compressed
from keras.models import load_model
from numpy import load
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC
# confirm mtcnn was installed correctly by loading it
import mtcnn
# print version
print(mtcnn.__version__)
# Importing required libraries for face detection with mtcnn on a photograph
from matplotlib import pyplot
from matplotlib.patches import Rectangle
from matplotlib.patches import Circle
from mtcnn.mtcnn import MTCNN
import scipy.misc




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

def save_faces(filename, pixels,result_list,required_size=(160, 160)):
    detectedFaces = list()
    # load the image
    data = pyplot.imread(filename)
    # plot each face as a subplot
    numOfStudents = 0
    for i in range(len(result_list)):
        numOfStudents = numOfStudents+1
        # get coordinates
        x1, y1, width, height = result_list[i]['box']
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        # extract the face
        face = pixels[y1:y2, x1:x2]
        # resize pixels to the model size
        image = Image.fromarray(face)
        image = image.resize(required_size)
        face_array = asarray(image)
        detectedFaces.append(face_array)
        print(face_array.shape)
        name = "face"+str(i)
        #scipy.misc.imsave(name, face_array)
        print(name, "Saved")
        #pyplot.savefig(axi, dpi=200)    
    # show the plot
    pyplot.show()
    print("Total Number of faces found :",numOfStudents)
    print(type(detectedFaces))
    return detectedFaces

# get the face embedding for one face
def get_embedding_Predict(model, face_pixels):
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




def getFaceEmbeddings(filename):
	# load image from file
	pixels = pyplot.imread(filename)
	# Create a folder to save the faces
	#os.mkdir('faces')
	# create the detector, using default weights
	detector = MTCNN()
	embeddingModel = load_model('Data/facenet_keras.h5')
	# detect faces in the image
	detected_faces = detector.detect_faces(pixels)
	# display faces on the original image
	processedFaces = save_faces(filename,pixels,detected_faces)
	print("Face Processed")
	faceListToTest = list()
	faceListToTest.extend(processedFaces)
	faceListToTest = asarray(faceListToTest)
	# convert each new face in the faceListToTest set to an embedding
	newEmbeddings = list()
	for face_pixels in faceListToTest:
		embedding = get_embedding(embeddingModel, face_pixels)
		newEmbeddings.append(embedding)
	newEmbeddings = asarray(newEmbeddings)
	return newEmbeddings