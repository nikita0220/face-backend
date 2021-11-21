from FaceRecognition import FaceAPI
import base64
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

face = FaceAPI()

@app.route('/testImage/', methods=['POST'])
def authenticate():
	print(request.files.get('image'))
	img = request.files.get('image')
	img.save('uploads/test.jpg')
	#img = request.files['testImage']
	#console.log(img)
	return {'result': 1}
	

@app.route('/reindex', methods=['GET'])
def reindex():
	groupName = request.args.get("groupName")
	face.trainGroup(groupName)
	return {'RESULT' : 'Success'}

@app.route('/addPerson/', methods=['POST'])
def addPerson():
	data = request.get_json()
	print('here', data)
	
	personName = data.get('name')
	groupName = data.get('group')
	personObject = face.addToGroup(groupName, personName)
	return personObject.person_id

@app.route('/addFace/', methods=['POST'])
def addFace():
	data = request.get_json()
	print('here', data)
	
	personId = data.get('personId')
	groupName = data.get('group')
	faceImage = data.get('face')
	face.addFaceToPerson(groupName, personId)
	return

@app.route('/createGroup/', methods=['POST'])
def createGroup():
	data = request.get_json()
	groupName = data.get('groupName')
	face.createNewGroup(groupName)
	return

@app.route('/detectFaces/', methods=['POST'])
def detectFaces():
	img = request.files.get('image')
	#groupName = request.args.get('groupName')
	groupName = 'random-group-03'
	print('Testing: ', groupName)
	result = face.detectFaces(img, groupName)
	return {'result' : result}



@app.route('/')
def index():
	return "<h1> ** == Face Recognition Server == ACTIVE **</h1>"



if __name__ == '__main__':
	app.run(threaded=True, port=5000)