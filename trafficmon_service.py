import pygame
import json
import cv2
import numpy as np
import urllib as ur
import random
import time
from algorithm_factory import Factory as algFac
import gdbm as dbm
import pickle
import os

class User:
	def __init__(self, uid):
		self.user_id = uid
		self.cameras = list()
		
	def add_cameras(self, cams):
		self.cameras = cams

	def register_camera(self, cam):
		if(cam not in self.cameras):
			self.cameras.append(cam)
		return cam

	def get_cameras(self):
		return self.cameras

class Camera:
	def __init__(self, name=None, url=None, interval=0.0, prev_image=False, dbm_input=None):
		if(dbm_input != None):
			self.init_dbm(dbm_input)
		else:
			self.subset = False
			self.name = name
			self.url = url
			self.alg = algFac.get_alg("none")

		self.update_interval = interval
		self.image = False
		self.prev_image = prev_image
		self.last_updated = time.time()
		self.path = ""
		self.update()
		
	def init_dbm(self, dbm_repr):
		self.name = dbm_repr["name"]
		self.subset = dbm_repr["subset"]
		self.url = dbm_repr["url"]
		self.update_interval = dbm_repr["interval"]
		self.alg = algFac.get_alg(dbm_repr["algorithm"])
		

	def get_dbm(self):
		json_repr = dict()
		json_repr["name"] = self.name
		json_repr["subset"] = self.subset
		json_repr["url"] = self.url
		json_repr["interval"] = self.update_interval
		json_repr["algorithm"] = self.alg.id
		return json.dumps(json_repr)

	def update(self):
		self.last_updated = time.time()
		(f,h) = ur.urlretrieve(self.url)
		tempImage = cv2.imread(f)
		if(self.subset):
			tempImage = tempImage[self.subset[1][0]:self.subset[1][1], self.subset[0][0]:self.subset[0][1]]
		if(isinstance(tempImage, np.ndarray) and isinstance(self.image, np.ndarray) and tempImage.shape == self.image.shape):
			if(np.bitwise_xor(tempImage, self.image).any()):
				self.prev_image = self.image
				self.image = tempImage
		elif(isinstance(self.image, bool)):
			self.image = tempImage
		elif(tempImage.shape != self.image.shape):
			self.image = tempImage
		self.image = self.alg.process(self.image, self.prev_image)
		self.path = os.path.basename(os.path.normpath(f))
		cv2.imwrite('static/' + self.path,self.image)
			

	def set_subset(self, x, y):
		self.subset = ((x[0],x[1]), (y[0],y[1]))

	def get_image(self):
		return self.image

	def set_algorithm(self, algorithm):
		self.alg = algorithm

	def get_keypoints(self):
		return self.alg.keypoints

	def get_image_keypoints(self):
		return cv2.drawKeypoints(self.image, self.alg.keypoints)

class Manager():
	def __init__(self, filename="default"):
		self.users = dict()
		self.cameras = dict()
		self.maxCamId = 0
		self.algorithms = algFac
		self.filename=filename
		
		self.user_db = dbm.open(filename + ".user", 'cs')
		self.camera_db = dbm.open(filename + ".camera", 'cs')
		
		self._load_from_file()
		
	
	def add_user(self, name):
		if(name in self.users):
			return 0
		else:
			self.users[name] = User(name)
			self._save_to_file()
			return 1
	
	def add_camera(self, cam_name, cam_url, subset=None, algorithm=None):
		newCamera = Camera(name=cam_name, url=cam_url)
		if(subset):
			newCamera.set_subset(subset[0], subset[1])
		if(algorithm):
			newCamera.set_algorithm(self.algorithms.get_alg(algorithm))
			
		self.cameras[str(self.maxCamId)] = newCamera
		self.maxCamId += 1
		self._save_to_file()
		return self.maxCamId - 1
	
	def subscribe_camera(self, user, cam):
		self.users[user].register_camera(cam)
		self._save_to_file()
	
	def _load_from_file(self):
		key = self.camera_db.firstkey()
		print(key)
		while key != None:
			if(int(key) >= self.maxCamId):
				self.maxCamId = int(key) + 1
			self.cameras[key] = Camera(dbm_input=json.loads(self.camera_db[key]))
			key = self.camera_db.nextkey(key)
			
		key = self.user_db.firstkey()
		while key != None:
			self.users[key] = User(key)
			self.users[key].add_cameras(json.loads(self.user_db[key]))
			key = self.user_db.nextkey(key)

	def _save_to_file(self):
		for (key,value) in self.cameras.items():
			self.camera_db[key] = value.get_dbm()
			
		for (key, value) in self.users.items():
			self.user_db[key] = json.dumps(value.get_cameras())
			
	def update_cameras(self, user_id):
		for cam_id in self.users[user_id].get_cameras():
			camera = self.cameras[cam_id]
			if(time.time() - camera.last_updated > camera.update_interval):
				camera.update()

	def test(self):
		return "Testing Manager"

if __name__ == "__main__":
	man = Manager()
	#man.add_user("Edvard")
	#cid = man.add_camera("Rundkjoring breivika", "http://weather.cs.uit.no/cam/cam_east.jpg", ((800,1200),(500,670)), "traffic")
	#man.subscribe_camera("Edvard", "0")
	print(man.cameras)
	
	print(man.cameras["0"].get_dbm())
	
	print(man.users["Edvard"].cameras)

	man.update_cameras("Edvard")
	for cam in man.users["Edvard"].cameras:
		man.cameras[cam].update()
		cv2.namedWindow(man.cameras[cam].url, cv2.CV_WINDOW_AUTOSIZE)
		cv2.imshow(man.cameras[cam].url, man.cameras[cam].get_image())
	cv2.waitKey()
