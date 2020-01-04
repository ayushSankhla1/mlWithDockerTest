# ToDo
# get the image -> Done
# extract the faces in the image -> Done
# convert the faces into the embeddings -> Done
# get prediction for each face by the embeddings -> Done
# return the predictions 
from Prediction.ImageEmbedding import getFaceEmbeddings
from Prediction.getPeoplesNames import getNames
from sklearn.preprocessing import Normalizer
import pickle
import os
from AWS.getData import get_model

def identify(MODEL_BUCKET_NAME, model_location, imageAddress):
	#imageAddress = "data/newPersonTest.JPG"
	# imageAddress = "data/finalTest.JPG"
	#cv2.imwrite(imageAddress, image) 
	#Convert the image into facenet embedding
	newEmbeddings = getFaceEmbeddings(imageAddress)
	#normalize input vectors
	in_encoder = Normalizer(norm='l2')
	newEmbeddings = in_encoder.transform(newEmbeddings)
	filename = "SVM_model.h5"
	model_location = model_location + filename
	#  Downloading the model if not already downloaded
	if os.path.exists(filename):
		# Update the code to manage updates
		print("no need to download")
	else:
		print("The file does not exist")
		get_model(MODEL_BUCKET_NAME, model_location, filename)
		print("Downloading completed")
	model =  pickle.load(open(filename, 'rb'))
	
	#Finding the index of the people
	result = model.predict(newEmbeddings)
	print(model.predict_proba(newEmbeddings))
	# print("Indexes of the people")
	# print(result) 
	#Finding the predicted names
	print(result)
	# names = getNames(result)
	# print(names)
	# return names
	return result