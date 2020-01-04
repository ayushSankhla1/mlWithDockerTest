# imports for AWS
import boto3
from boto3 import client
import logging
from botocore.exceptions import ClientError

def get_image(BUCKET_NAME, S3_FILENAME,location):
	"""Retrieve an object from an Amazon S3 bucket

	:param bucket_name: string
	:param object_name: string
	:return: botocore.response.StreamingBody object. If error, return None.
	"""
	location = location+'my_temp_image.jpg'
	s3 = boto3.resource('s3')
	# print("in get_image and resource loaded")

	try:
		s3.Bucket(BUCKET_NAME).download_file(S3_FILENAME,location )
		print("Got image")
	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Code'] == "404":
			print("The object does not exist.")
		else:
			raise
	return location


def get_extracted_faces(BUCKET_NAME, S3_FILENAME,location):
	"""Retrieve an object from an Amazon S3 bucket

	:param bucket_name: string
	:param object_name: string
	:return: botocore.response.StreamingBody object. If error, return None.
    """
	location = location+'faceData.npz'
	s3 = boto3.resource('s3')
	try:
		s3.Bucket(BUCKET_NAME).download_file(S3_FILENAME,location )
		print("Got face Data")
	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Code'] == "404":
			print("The object does not exist.")
		else:
			raise
	return location

def get_embeddings(BUCKET_NAME, S3_FILENAME,location):
	"""Retrieve an object from an Amazon S3 bucket

	:param bucket_name: string
	:param object_name: string
	:return: botocore.response.StreamingBody object. If error, return None.
    """
	location = location+'embeddings.npz'
	s3 = boto3.resource('s3')
	try:
		s3.Bucket(BUCKET_NAME).download_file(S3_FILENAME,location )
		print("Got face Data")
	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Code'] == "404":
			print("The object does not exist.")
		else:
			raise
	return location

def get_model(BUCKET_NAME, S3_FILENAME, location):
	"""Retrieve an object from an Amazon S3 bucket

	:param bucket_name: string
	:param object_name: string
	:return: botocore.response.StreamingBody object. If error, return None.
    """
	
	s3 = boto3.resource('s3')
	try:
		s3.Bucket(BUCKET_NAME).download_file(S3_FILENAME,location )
		print("Got trained model")
	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Code'] == "404":
			print("The object does not exist.")
		else:
			raise
	return location

