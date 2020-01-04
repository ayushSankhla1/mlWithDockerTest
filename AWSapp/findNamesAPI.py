import os
import flask
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse

from Prediction.identifyPerson import identify
from keras import backend as K

# import numpy as np
# from numpy import load
# # import PIL 
import cv2 
# import io
import werkzeug


app = Flask(__name__)
api = Api(app)
paraser = reqparse.RequestParser()


class MakePrediction(Resource):
	def get():
		return {'message':'connected successfully'}

	@staticmethod
	def post():
		names = list()
		
		paraser.add_argument('image',type=werkzeug.datastructures.FileStorage,location='files')
		args = paraser.parse_args()
		imageFile = args['image']
		#Save file and save the location in imageAddress 
		img_address = "Data/finalTest.JPG"
		imageFile.save(img_address)
		print("Got image")
		MODEL_BUCKET_NAME = 'iutkarshstudentfacemodel'
		folderAddress = "testSchool01/"
		names = identify(MODEL_BUCKET_NAME, folderAddress, img_address) # <- It is running
		# names = ['ayush','sankhla']
		print(names)
		names = names.tolist()
		K.clear_session()
		# Delete file from location -----------------
		if os.path.exists(img_address):
			os.remove(img_address)
		else:
			print("The file does not exist") 
		return jsonify({
			'Names': names
		})


api.add_resource(MakePrediction, '/predict')
if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')
