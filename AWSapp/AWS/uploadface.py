# imports for AWS S3
import boto3
from boto3 import client
import logging
from botocore.exceptions import ClientError

# imports for MongoDB
from pymongo import MongoClient
from random import randint
def put_object(dest_bucket_name, dest_object_name, src_data):
	"""Add an object to an Amazon S3 bucket

	The src_data argument must be of type bytes or a string that references
	a file specification.

	:param dest_bucket_name: string
	:param dest_object_name: string
	:param src_data: bytes of data or string reference to file spec
	:return: True if src_data was added to dest_bucket/dest_object, otherwise
	False
	"""

	# Construct Body= parameter
	if isinstance(src_data, bytes):
		object_data = src_data
	elif isinstance(src_data, str):
		try:
			object_data = open(src_data, 'rb')
			# possible FileNotFoundError/IOError exception
		except Exception as e:
			# logging.error(e)
			return False
	else:
		# logging.error('Type of ' + str(type(src_data)) +' for the argument \'src_data\' is not supported.')
		return False
	# Put the object
	s3 = boto3.client('s3')
	try:
		s3.put_object(Bucket=dest_bucket_name, Key=dest_object_name, Body=object_data)
	except ClientError as e:
		# AllAccessDisabled error == bucket not found
		# NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
		# logging.error(e)
		return False
	finally:
		if isinstance(src_data, str):
			object_data.close()
	return True

def update_location(db,id, new_loc):
	for eachPath in new_loc:
		db.photoCollection.update({'id': id}, {'$push': {'location': eachPath}})


def uploadFaceImage(BUCKET_NAME,S3_img_address,local_img_address,studentID):
	print("In uploadFaceImage")
	client = MongoClient(port=27017)
	db=client.business
	print("Conncted to database")
	pathArray = []
	isUploadSuccessfull = put_object(BUCKET_NAME,S3_img_address,local_img_address)
	if isUploadSuccessfull:
		pathArray.append(S3_img_address)
	get = db.photoCollection.find({'id': studentID})
	i = 0
	print("responce from mongodb")
	for element in get:
		i+=1
		#print(element)
	# print(i)
	data = {'id':studentID,
			'location': pathArray
	}
	if i==0:
		result = db.photoCollection.insert_one(data)
		print("Inserting for first time")
	else:
		print("Updating data")
		update_location(db,studentID,pathArray)
	print("Data inserted")