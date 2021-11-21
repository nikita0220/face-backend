import base64
import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person


KEY = "d0ba59dbcb5542a6bf857925925485c9"
ENDPOINT = "https://face-api-backend.cognitiveservices.azure.com/"



class FaceAPI:
    def __init__(self):
        self.face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

    def createNewGroup(self, groupName):
        PERSON_GROUP_ID = groupName
        self.face_client.person_group.create(person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID)

    def addToGroup(self, groupName, personName):
        personObject = self.face_client.person_group_person.create(groupName, personName)
        return personObject

    def addFaceToPerson(self, groupName, personObject, faceImage):

        self.face_client.person_group_person.add_face_from_stream(groupName, personObject.person_id, faceImage)
        print('HH', self.face_client.person_group_person.get(groupName, personObject.person_id))


    def trainGroup(self, groupName):
        print('Training the person group...')
        self.face_client.person_group.train(groupName)

        while (True):
            training_status = self.face_client.person_group.get_training_status(groupName)
            print("Training status: {}.".format(training_status.status))

            if (training_status.status is TrainingStatusType.succeeded):
                break
            elif (training_status.status is TrainingStatusType.failed):
                self.face_client.person_group.delete(person_group_id=groupName)
                sys.exit('Training the person group has failed.')
            time.sleep(5)

    def detectFaces(self, image, groupName):
        faces = self.face_client.face.detect_with_stream(image, detection_model='detection_03')
        face_ids = []
        print(groupName)
        for face in faces:
            face_ids.append(face.face_id)
        return face_ids

        results = self.face_client.face.identify(face_ids, groupName)
        return results



class SampleUser:
    def __init__(self, groupName, status):
        self.groupName = groupName
        self.face = FaceAPI()

        if status == 'NEW':
            self.createNewGroup()

    def createNewGroup(self):
        self.face.createNewGroup(self.groupName)

    def loadData_and_train(self):
        woman = self.face.addToGroup(self.groupName, 'Woman')
        man = self.face.addToGroup(self.groupName, 'Man')
        child = self.face.addToGroup(self.groupName, 'Child')

        #Load
        woman_images = [file for file in glob.glob('*.jpg') if file.startswith("w")]
        man_images = [file for file in glob.glob('*.jpg') if file.startswith("m")]
        child_images = [file for file in glob.glob('*.jpg') if file.startswith("ch")]

        for image in woman_images:
            w = open(image, 'r+b')
            self.face.addFaceToPerson(self.groupName, woman, w)

        for image in man_images:
            m = open(image, 'r+b')
            self.face.addFaceToPerson(self.groupName, man, m)

        for image in child_images:
            ch = open(image, 'r+b')
            self.face.addFaceToPerson(self.groupName, child, ch)

        self.face.trainGroup(self.groupName)


    def loadFromCloud(self):
        woman = self.face.addToGroup(groupName, 'Woman')
        man = self.face.addToGroup(groupName, 'Man')
        child = self.face.addToGroup(groupName, 'Child')




    def testSampleImage(self):
        test_image_array = glob.glob('test-image-person-group.jpg')
        image = open(test_image_array[0], 'r+b')

        print('Pausing for 60 seconds to avoid triggering rate limit on free account...')
        time.sleep (30)

        results = self.face.detectFaces(image, self.groupName)
        print(results)

        # face_ids = []
        # faces = self.face.face_client.face.detect_with_stream(image, detection_model='detection_03')
        # for face in faces:
        #     face_ids.append(face.face_id)

        # results = self.face.face_client.face.identify(face_ids, self.groupName)
        # print('Identifying faces in {}'.format(os.path.basename(image.name)))
        # if not results:
        #     print('No person identified in the person group for faces from {}.'.format(os.path.basename(image.name)))
        # for person in results:
        #     if len(person.candidates) > 0:
        #         print('Person for face ID {} is identified in {} with a confidence of {}.'.format(person.face_id, os.path.basename(image.name), person.candidates[0].confidence)) # Get topmost confidence score
        #     else:
        #         print('No person identified for face ID {} in {}.'.format(person.face_id, os.path.basename(image.name)))   



if __name__ == '__main__':

#     # with open('test-image-person-group.jpg', "rb") as image_file:
#     #     encoded_string = base64.b64encode(image_file.read())

#     #print(encoded_string)
    #Existing User
    groupName = 'random-group-03'
    user = SampleUser(groupName, 'OLD')
    user.testSampleImage()

    #New User
    # groupName = 'random-group-08'
    # user = SampleUser(groupName, 'NEW')
    # user.testSampleImage()