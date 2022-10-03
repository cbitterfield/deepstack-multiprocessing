#!/usr/bin/env python3


print("Deleting all faces registerin Deepstack")
import requests
faces = requests.post("http://localhost:32168/v1/vision/face/list").json()
print("Faces found {}".format(len(faces['faces'])))

for face in faces['faces']:
	print(face)
	response = requests.post("http://localhost:32168/v1/vision/face/delete",data={"userid":face}).json()
	print("Deleting face = {} | {}".format(face,response))
	
	
