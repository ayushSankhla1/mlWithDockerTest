# For testing purpose only
# Upload files from local directory to s3 bucket for AWS code testing 

from os import listdir
import numpy as np

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

def upload_files(BUCKET_NAME,S3_FILENAME,SOURCE_FILENAME):
    # Set up logging
    # logging.basicConfig(level=logging.DEBUG,format='%(levelname)s: %(asctime)s: %(message)s')

    # Put the object into the bucket
    success = put_object(BUCKET_NAME, S3_FILENAME, SOURCE_FILENAME)
    path = []
    if success:
        # logging.info(f'Added {S3_FILENAME} to {BUCKET_NAME}')
        print(SOURCE_FILENAME, " uploaded successfully")
        return True
    else:
        return False    

def update_location(db,id, new_loc):
    for eachPath in new_loc:
        db.photoCollection.update({'id': id}, {'$push': {'location': eachPath}})


def upload_faces(BUCKET_NAME,directory,subdir):
    client = MongoClient(port=27017)
    db=client.business
    print("Conncted to database")
    pathArray = []
    for filename in listdir(directory):
        # path
        path = directory + filename
        # get face
        # print("uploading the file at", path)
        isUploadSuccessfull = upload_files(BUCKET_NAME,path,path)
        if isUploadSuccessfull:
            pathArray.append(path)

    get = db.photoCollection.find({'id': subdir})
    i = 0
    print("responce from mongodb")
    for element in get:
        i+=1
        #print(element)
    # print(i)
    data = {'id':subdir,
            'location': pathArray
    }
    # print(type(location))
    # location = np.asarray(location)
    # print(location.shape)
    # print(location)
    if i==0:
        result = db.photoCollection.insert_one(data)
        print("Inserting for first time")
    else:
        print("Updating data")
        update_location(db,subdir,pathArray)
    print("Data inserted")
		

def load_test_data(BUCKET_NAME,directory):
	for subdir in listdir(directory):
		# path
		path = directory + subdir + '/'
		upload_faces(BUCKET_NAME,path,subdir)


# load_test_data('iutkarshstudentimages','testSchool01/')